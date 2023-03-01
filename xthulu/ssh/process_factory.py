"""SSH server process factory"""

# stdlib
from asyncio import gather, IncompleteReadError, Queue, TimeoutError, wait_for
from datetime import datetime
from multiprocessing.connection import Pipe
from multiprocessing import Process

# 3rd party
from asyncssh import SSHServerProcess, TerminalSizeChanged

# local
from ..configuration import get_config
from ..events.structs import EventData
from ..logger import log
from .context import SSHContext
from .exceptions import Goto, ProcessClosing
from .structs import Script
from .terminal import terminal_process
from .terminal.proxy_terminal import ProxyTerminal


async def handle_client(proc: SSHServerProcess):
    """
    Factory method for handling client connections.

    Args:
        proc: The server process responsible for the client.
    """

    cx = SSHContext(proc=proc)
    await cx._init()

    if proc.subsystem:
        log.error(
            f"{cx.whoami} requested unimplemented subsystem: "
            f"{proc.subsystem}"
        )
        proc.channel.close()
        proc.close()

        return

    termtype = proc.get_terminal_type()

    if termtype is None:
        proc.channel.close()
        proc.close()

        return

    if "LANG" not in proc.env or "UTF-8" not in proc.env["LANG"]:
        cx.encoding = "cp437"

    if "TERM" not in cx.env:
        cx.env["TERM"] = termtype

    w, h, pw, ph = proc.get_terminal_size()
    cx.env["COLUMNS"] = str(w)
    cx.env["LINES"] = str(h)
    proxy_pipe, subproc_pipe = Pipe()
    session_stdin = Queue()
    timeout = int(get_config("ssh.session.timeout", 120))
    await cx.user.update(last=datetime.utcnow()).apply()  # type: ignore

    async def input_loop():
        """Catch exceptions on stdin and convert to EventData."""

        while True:
            try:
                if timeout > 0:
                    r = await wait_for(proc.stdin.readexactly(1), timeout)
                else:
                    r = await proc.stdin.readexactly(1)

                await session_stdin.put(r)

            except IncompleteReadError:
                # process is likely closing; end the loop
                return

            except TimeoutError:
                log.warning(f"{cx.whoami} timed out")
                cx.echo(
                    "".join(
                        (
                            cx.term.normal,
                            "\r\n",
                            cx.term.bold_white_on_red(" TIMED OUT "),
                            cx.term.normal,
                            "\r\n",
                        )
                    )
                )
                proc.channel.close()
                proc.close()

                return

            except TerminalSizeChanged as sz:
                cx.env["COLUMNS"] = str(sz.width)
                cx.env["LINES"] = str(sz.height)
                cx.term._width = sz.width
                cx.term._height = sz.height
                cx.term._pixel_width = sz.pixwidth
                cx.term._pixel_height = sz.pixheight
                await cx.events.put(EventData("resize", (sz.width, sz.height)))

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
        top_names: list[str] = get_config("ssh.userland.top", ("top",))
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

            if proc.channel:
                proc.channel.close()

            proc.close()

    log.info(f"{cx.whoami} starting terminal session")

    try:
        await gather(input_loop(), main_process())
    finally:
        if proc.channel:
            proc.channel.close()

        proc.close()
