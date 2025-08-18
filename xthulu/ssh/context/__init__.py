"""xthulu context class module"""

# type checking
from typing import Any, Callable, NoReturn, Optional

# stdlib
from asyncio import Queue, sleep
from codecs import decode
from functools import partial, singledispatch
from logging import LoggerAdapter
from subprocess import Popen, PIPE

# 3rd party
from asyncssh import SSHServerProcess
from sqlmodel import func, select

# local
from ... import locks
from ...events import EventQueue
from ...logger import log
from ...models import User
from ...resources import db_session
from ...scripting import load_userland_module
from ..console import XthuluConsole
from ..exceptions import Goto, ProcessClosing, ProcessForciblyClosed
from ..structs import Script
from .lock_manager import _LockManager
from .logger_adapter import ContextLoggerAdapter


class SSHContext:
    """Context object for SSH sessions"""

    proc: SSHServerProcess
    """This context's containing process"""

    input: Queue
    """This context's input queue"""

    stack: list[Script] = []
    """Script stack"""

    console: XthuluConsole
    """Context terminal object"""

    encoding: str
    """Encoding for session"""

    user: User
    """Context user object"""

    username: str
    """Connected user's name"""

    ip: str
    """Remote IP address"""

    sid: str
    """Internal session ID"""

    whoami: str
    """username@host string for session"""

    log: LoggerAdapter
    """Context logger instance"""

    events: EventQueue
    """Events queue for session"""

    env: dict[str, str]
    """Environment variables"""

    _peername: list[str]

    @classmethod
    async def _create(cls, proc: SSHServerProcess, encoding="utf-8"):
        """
        Factory method for instantiating a new context asynchronously.

        Args:
            proc: The parent process.
            encoding: The session encoding.

        Returns:
            A new `xthulu.ssh.context.SSHContext` object.
        """

        self = SSHContext()
        self._peername = proc.get_extra_info("peername")
        self.sid = "{}:{}".format(*self._peername)
        self.username = proc.get_extra_info("username")
        self.ip = self._peername[0]
        self.whoami = f"{self.username}@{self.sid}"
        self.proc = proc
        self.input = Queue(1024)
        self.encoding = encoding
        self.log = ContextLoggerAdapter(
            log.getChild(self.sid), {"whoami": self.whoami}
        )
        self.events = EventQueue(self.sid)
        self.env = dict(proc.env)

        async with db_session() as db:
            self.user = (
                await db.exec(
                    select(User).where(
                        func.lower(User.name) == self.username.lower()
                    )
                )
            ).one()

        return self

    def echo(self, *args: str, encoding: Optional[str] = None):
        """
        Echo text to the terminal.

        Args:
            args: The text to echo. Multiple args will be joined without line \
                breaks or whitespace.
            encoding: The encoding to use for output. If unspecified, the \
                context's encoding will be used.
        """

        if not args:
            return

        text: list[str] = []

        for string in args:
            encoded = (
                decode(bytes(string, encoding), encoding=encoding)
                if encoding is not None
                else string
            )
            text.append(encoded)

        if encoding is not None:
            self.proc.stdout.write("".join(text).encode(self.encoding))
        else:
            self.console.print("".join(text), sep="", end="")

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

        return locks.get(self.sid, name)

    async def inkey(self, text="", spinner="dots", timeout=0.0) -> bytes | None:
        """
        Wait for (and return) a keypress.

        Args:
            text: The prompt text, if any.
            spinner: The prompt spinner (if `text` is specified).
            timeout: The length of time (in seconds) to wait for input. A \
                value of `0` will wait forever.
        """

        from ..console.internal.input import wait_for_key

        if self.encoding != "utf-8":
            spinner = "line"

        return await wait_for_key(self, text, spinner, timeout)

    def release_lock(self, name: str) -> bool:
        """
        Release lock on behalf of session user.

        Args:
            name: The name of the lock to release.

        Returns:
            Whether or not the lock was valid to begin with.
        """

        return locks.release(self.sid, name)

    async def redirect(self, proc: Popen | list | tuple | str):
        """
        Redirect context IO to other process; convenience method which wraps
        AsyncSSH's redirection routine.

        Args:
            proc: The process to redirect to.
        """

        @singledispatch
        async def f(proc: Popen | tuple | list | str):
            raise NotImplementedError("proc must be Popen, tuple, list, or str")

        @f.register(Popen)
        async def _(proc: Popen) -> NoReturn:  # type: ignore
            await self.proc.redirect(
                stdin=proc.stdin,
                stdout=proc.stdout,
                stderr=proc.stderr,
                send_eof=False,
            )
            # drain any remaining IO buffer data to avoid tainting context IO
            await self.proc.stdout.drain()
            await self.proc.stderr.drain()
            # reconnect stdin (or else input freezes)
            await self.proc.redirect(stdin=PIPE)

        @f.register(tuple)
        @f.register(list)
        @f.register(str)
        async def _(proc: tuple | list | str) -> NoReturn:  # type: ignore
            p = Popen(
                proc,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
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

        try:
            mod = load_userland_module(script.name)
            main: Callable[..., Any] = getattr(mod, "main")
            return await main(self, *script.args, **script.kwargs)
        except (ProcessClosing, ProcessForciblyClosed, Goto):
            raise
        except Exception:
            message = f"Exception in script {script.name}"
            log.exception(message, extra={"user": self.username})
            self.echo(f"\n\n[bright_white on red] {message} [/]\n\n")
            await sleep(3)
            # avoid input debuffering bug if a Textual app crashed
            self.proc.stdin.feed_data(b"\x1b")
