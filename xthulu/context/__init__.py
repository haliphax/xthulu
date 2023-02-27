"""xthulu context class module"""

# type checking
from typing import Any, Callable, Final, NoReturn, Optional

# stdlib
import asyncio as aio
from codecs import decode
from functools import partial, singledispatch
from imp import find_module, load_module
import logging
import subprocess
import sys
from typing import List, Tuple, Union

# 3rd party
from asyncssh import SSHServerProcess
from sqlalchemy import func

# local
from .. import config, locks, log as syslog
from ..events import EventQueue
from ..exceptions import Goto, ProcessClosing
from ..models import User
from ..structs import Script
from ..terminal import ProxyTerminal
from .lock_manager import _LockManager
from .log_filter import ContextLogFilter


class Context(object):
    """Context object for SSH sessions"""

    stack = []
    """Script stack"""

    user: User
    """User object (assigned at _init)"""

    term: ProxyTerminal
    """Context terminal object"""

    _sid: Final[str]
    """Internal session ID"""

    def __init__(self, proc, encoding="utf-8"):
        _peername = proc.get_extra_info("peername")
        _username = proc.get_extra_info("username")
        self._sid = "{}:{}".format(*_peername)

        self.proc: SSHServerProcess = proc
        """SSHServerProcess for session"""

        self.encoding: str = encoding
        """Encoding for session"""

        self.ip: str = _peername[0]
        """Remote IP address"""

        self.log: logging.Logger = logging.getLogger(self.sid)
        """Logging facility"""

        self.events: EventQueue = EventQueue(self.sid)
        """Events queue"""

        self.env: dict = proc.env.copy()
        """Environment variables"""

        # set up logging
        if not self.log.filters:
            self.log.addFilter(ContextLogFilter(_username, self.ip))
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(
                logging.Formatter(
                    "{asctime} {levelname:<7} {module}.{funcName}: "
                    "{username}@{ip} {message}",
                    style="{",
                )
            )
            self.log.addHandler(streamHandler)
            self.log.setLevel(syslog.getEffectiveLevel())

    async def _init(self):
        """Asynchronous initialization routine"""

        _username = self.proc.get_extra_info("username")
        """Internal username"""

        self.user: User = await User.query.where(
            func.lower(User.name) == _username.lower()
        ).gino.first()
        """Session user object"""

        self.log.debug(repr(self.user))

    # read-only
    @property
    def sid(self) -> str:
        """Session ID (IP:PORT)"""

        return self._sid

    def echo(self, text: str, encoding: Optional[str] = None):
        """
        Echo text to the terminal.

        Args:
            text: The text to echo.
            encoding: The encoding to use for output. If unspecified, the
                context's encoding will be used.
        """

        if text is None:
            return

        if encoding is not None:
            text = decode(bytes(text, encoding), encoding)

        self.proc.stdout.write(text.encode(self.encoding))

    async def gosub(self, script: str, *args, **kwargs) -> Any:
        """
        Execute script and return result.

        Args:
            script: The userland script to execute.

        Returns:
            The return value of the script, if any.
        """

        to_run = Script(script, args, kwargs)

        return await self.runscript(to_run)

    def goto(self, script: Script, *args, **kwargs):
        """
        Switch to script and clear stack.

        Args:
            script: The userland script to execute.
        """

        raise Goto(script, *args, **kwargs)

    @property
    def lock(self) -> partial[_LockManager]:
        """
        Session lock context manager.

        Args:
            name: The name of the lock to attempt.

        Returns:
            Whether or not the lock was granted.
        """

        return partial(_LockManager, self.sid)

    def get_lock(self, name: str) -> bool:
        """
        Acquire lock on behalf of session user.

        Args:
            name: The name of the lock to attempt.

        Returns:
            Whether or not the lock was granted.
        """

        return locks.get(self.sid, name)

    def release_lock(self, name: str) -> bool:
        """
        Release lock on behalf of session user.

        Args:
            name: The name of the lock to release.

        Returns:
            Whether or not the lock was valid to begin with.
        """

        return locks.release(self.sid, name)

    async def redirect(self, proc: Union[subprocess.Popen, List, Tuple, str]):
        """
        Redirect context IO to other process; convenience method which wraps
        AsyncSSH's redirection routine.

        Args:
            proc: The process to redirect to.
        """

        @singledispatch
        async def f(proc: subprocess.Popen | Tuple | List | str):
            raise NotImplementedError("proc must be Popen, tuple, list, or str")

        @f.register(subprocess.Popen)
        async def _(proc) -> NoReturn:  # type: ignore
            await self.proc.redirect(
                stdin=proc.stdin,
                stdout=proc.stdout,
                stderr=proc.stderr,
                send_eof=False,
            )
            await self.proc.stdout.drain()
            await self.proc.stderr.drain()
            await self.proc.redirect(stdin=subprocess.PIPE)

        @f.register(tuple)
        @f.register(list)
        @f.register(str)
        async def _(proc) -> NoReturn:  # type: ignore
            p = subprocess.Popen(
                proc,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=False,
            )
            await self.redirect(p)

        await f(proc)

    async def runscript(self, script: Script) -> Any:
        """
        Run script and return result; used by `goto` and `gosub`.

        Args:
            script: The userland script to run.

        Returns:
            The return value of the script, if any.
        """

        self.log.info(f"Running {script}")
        split = script.name.split(".")
        found = None
        mod = None

        for seg in split:
            if mod is not None:
                found = find_module(seg, list(mod.__path__))
            else:
                found = find_module(seg, config["ssh"]["userland"]["paths"])

            mod = load_module(seg, *found)  # type: ignore

        try:
            main: Callable = getattr(mod, "main")
            return await main(self, *script.args, **script.kwargs)
        except (ProcessClosing, Goto):
            raise
        except Exception as exc:
            self.log.exception(exc)
            self.echo(
                self.term.bold_red_on_black(  # type: ignore
                    f"\r\nException in {script.name}\r\n"
                )
            )
            await aio.sleep(3)
