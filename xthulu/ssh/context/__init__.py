"""xthulu context class module"""

# type checking
from typing import IO, Any, Callable, Final, NoReturn, Optional
from types import ModuleType

# stdlib
from asyncio import sleep
from codecs import decode
from functools import partial, singledispatch
from imp import find_module, load_module
import logging
import subprocess
import sys

# 3rd party
from asyncssh import SSHServerProcess
from sqlalchemy import func

# local
from ...configuration import get_config
from ...events import EventQueue
from ...logger import log
from ...models import User
from ..exceptions import Goto, ProcessClosing
from ..structs import Script
from ..terminal.proxy_terminal import ProxyTerminal
from .lock_manager import _LockManager
from .log_filter import ContextLogFilter


class SSHContext:

    """Context object for SSH sessions"""

    stack = []
    """Script stack"""

    term: ProxyTerminal
    """Context terminal object"""

    user: User
    """Context user object"""

    def __init__(self, proc, encoding="utf-8"):
        self._peername: Final[list[str]] = proc.get_extra_info("peername")

        self.sid: Final = "{}:{}".format(*self._peername)
        """Internal session ID"""

        self.username: Final = proc.get_extra_info("username")
        """Connected user's name"""

        self.ip: Final = self._peername[0]
        """Remote IP address"""

        self.whoami: Final = f"{self.username}@{self.ip}"
        """Connected user's username@host string"""

        self.proc: SSHServerProcess = proc
        """SSHServerProcess for session"""

        self.encoding: str = encoding
        """Encoding for session"""

        self.log: logging.Logger = logging.getLogger(self.sid)
        """Logging facility"""

        self.events: EventQueue = EventQueue(self.sid)
        """Events queue"""

        self.env: dict[str, str] = proc.env.copy()
        """Environment variables"""

        # set up logging
        if not self.log.filters:
            self.log.addFilter(ContextLogFilter(self.whoami))
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(
                logging.Formatter(
                    "{asctime} {levelname:<7} <{module}.{funcName}> {whoami} "
                    "{message}",
                    style="{",
                )
            )
            self.log.addHandler(streamHandler)
            self.log.setLevel(log.getEffectiveLevel())

    async def _init(self):
        """Asynchronous initialization routine."""

        self.user = await User.query.where(
            func.lower(User.name) == self.username.lower()
        ).gino.first()

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
            text = decode(bytes(text, encoding), encoding=encoding)

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

    def goto(self, script: str, *args, **kwargs) -> NoReturn:
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

        from ... import locks

        return locks.get(self.sid, name)

    def release_lock(self, name: str) -> bool:
        """
        Release lock on behalf of session user.

        Args:
            name: The name of the lock to release.

        Returns:
            Whether or not the lock was valid to begin with.
        """

        from ... import locks

        return locks.release(self.sid, name)

    async def redirect(self, proc: subprocess.Popen | list | tuple | str):
        """
        Redirect context IO to other process; convenience method which wraps
        AsyncSSH's redirection routine.

        Args:
            proc: The process to redirect to.
        """

        @singledispatch
        async def f(proc: subprocess.Popen | tuple | list | str):
            raise NotImplementedError("proc must be Popen, tuple, list, or str")

        @f.register(subprocess.Popen)
        async def _(proc: subprocess.Popen) -> NoReturn:  # type: ignore
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
        async def _(proc: tuple | list | str) -> NoReturn:  # type: ignore
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
        split: list[str] = script.name.split(".")
        found: tuple[IO[Any], str, tuple[str, str, int]] | None = None
        mod: ModuleType | None = None

        for seg in split:
            if mod is not None:
                found = find_module(seg, list(mod.__path__))
            else:
                found = find_module(seg, get_config("ssh.userland.paths"))

            mod = load_module(seg, *found)  # type: ignore

        try:
            main: Callable[..., Any] = getattr(mod, "main")
            return await main(self, *script.args, **script.kwargs)
        except (ProcessClosing, Goto):
            raise
        except Exception:
            message = f"Exception in script {script.name}"
            self.log.exception(message)
            self.echo(
                "".join(
                    (
                        self.term.normal,
                        "\r\n",
                        self.term.bold_white_on_red(f" {message} "),
                        self.term.normal,
                        "\r\n",
                    )
                )
            )
            await sleep(3)
