"""SSH server implementation"""

# stdlib
import asyncio as aio
from datetime import datetime
from multiprocessing import Pipe, Process

# 3rd party
import asyncssh
from sqlalchemy import func

# local
from .. import config, locks
from ..context import Context
from ..events import EventQueues
from ..exceptions import Goto, ProcessClosing
from ..models import User
from ..structs import EventData, Script
from ..terminal import terminal_process
from ..terminal.proxy_terminal import ProxyTerminal
from . import log


class SSHServer(asyncssh.SSHServer):

    """xthulu SSH Server"""

    _username: str | None = None

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        """
        Connection opened.

        Args:
            conn: The connection object.
        """

        self._peername: list[str] = conn.get_extra_info("peername")
        self._sid = "{}:{}".format(*self._peername)
        EventQueues.q[self._sid] = aio.Queue()
        log.info(f"{self._peername[0]} connecting")

    def connection_lost(self, exc: Exception):
        """
        Connection closed.

        Args:
            exc: The exception that caused the connection loss, if any.
        """

        del EventQueues.q[self._sid]
        locks.expire(self._sid)

        if exc:
            log.error(f"Error: {exc}")

        log.info(f"{self._username}@{self._peername[0]} disconnected")

    def begin_auth(self, username: str) -> bool:
        """
        Check for auth bypass.

        Args:
            username: The username to check.

        Returns:
            Whether authentication is necessary.
        """

        self._username = username
        pwd_required = True

        if (
            "no_password" in config["ssh"]["auth"]
            and username in config["ssh"]["auth"]["no_password"]
        ):
            log.info(f"No password required for {username}")
            pwd_required = False

        log.info(f"{username}@{self._peername[0]} connected")

        return pwd_required

    def password_auth_supported(self) -> bool:
        """Support password authentication."""

        return True

    async def validate_password(self, username: str, password: str) -> bool:
        """
        Validate provided password.

        Args:
            username: The username to validate.
            password: The password to validate.

        Returns:
            Whether the authentication is valid.
        """

        u = await User.query.where(
            func.lower(User.name) == username.lower()
        ).gino.first()

        if u is None:
            log.warn(f"User {username} does not exist")

            return False

        expected, _ = User.hash_password(password, u.salt)

        if expected != u.password:
            log.warn(f"Invalid credentials received for {username}")

            return False

        log.info(f"Valid credentials received for {username}")

        return True

    @classmethod
    async def handle_client(cls, proc: asyncssh.SSHServerProcess):
        """
        Client connected.

        Args:
            proc: The server process responsible for the client.
        """

        termtype = proc.get_terminal_type()

        if termtype is None:
            proc.channel.close()
            proc.close()
            return

        cx = Context(proc=proc)
        await cx._init()

        if "LANG" not in proc.env or "UTF-8" not in proc.env["LANG"]:
            cx.encoding = "cp437"

        if "TERM" not in cx.env:
            cx.env["TERM"] = termtype

        w, h, pw, ph = proc.get_terminal_size()
        cx.env["COLUMNS"] = w
        cx.env["LINES"] = h
        proxy_pipe, subproc_pipe = Pipe()
        session_stdin = aio.Queue()
        timeout = int(
            config.get("ssh", {}).get("session", {}).get("timeout", 120)
        )
        await cx.user.update(last=datetime.utcnow()).apply()  # type: ignore

        async def input_loop():
            """Catch exceptions on stdin and convert to EventData."""

            while True:
                try:
                    if timeout > 0:
                        r = await aio.wait_for(
                            proc.stdin.readexactly(1), timeout
                        )
                    else:
                        r = await proc.stdin.readexactly(1)

                    await session_stdin.put(r)

                except aio.IncompleteReadError:
                    return

                except aio.TimeoutError:
                    cx.echo(cx.term.bold_red_on_black("\r\nTimed out.\r\n"))
                    log.warning(f"{cx.user.name}@{cx.sid} timed out")
                    proc.channel.close()
                    proc.close()

                    return

                except asyncssh.misc.TerminalSizeChanged as sz:
                    cx.env["COLUMNS"] = sz.width
                    cx.env["LINES"] = sz.height
                    cx.term._width = sz.width
                    cx.term._height = sz.height
                    cx.term._pixel_width = sz.pixwidth
                    cx.term._pixel_height = sz.pixheight
                    await cx.events.put(
                        EventData(
                            "resize",
                            (
                                sz.width,
                                sz.height,
                            ),
                        )
                    )

        async def main_process():
            """Userland script stack; main process."""

            tp = Process(
                target=terminal_process,
                args=(termtype, w, h, pw, ph, subproc_pipe),
            )
            tp.start()
            cx.term = ProxyTerminal(
                session_stdin,
                proc.stdout,
                cx.encoding,
                proxy_pipe,
                w,
                h,
                pw,
                ph,
            )
            # prep script stack with top scripts;
            # since we're treating it as a stack and not a queue, add them
            # reversed so they are executed in the order they were defined
            top_names = (
                config.get("ssh", {}).get("userland", {}).get("top", ("top",))
            )
            cx.stack = [Script(s, (), {}) for s in reversed(top_names)]

            # main script engine loop
            try:
                while len(cx.stack):
                    try:
                        await cx.runscript(cx.stack.pop())
                    except Goto as goto_script:
                        cx.stack = [goto_script.value]
                    except ProcessClosing:
                        cx.stack = []
            finally:
                # send sentinel to close child 'term_pipe' process
                proxy_pipe.send((None, (), {}))
                proc.channel.close()
                proc.close()

        await aio.gather(input_loop(), main_process(), return_exceptions=True)
