"""SSH server process factory"""

# stdlib
from asyncio import gather, IncompleteReadError, wait_for
from datetime import datetime

# 3rd party
from asyncssh import SSHServerProcess, TerminalSizeChanged

# local
from ..configuration import get_config
from ..events.structs import EventData
from .console import XthuluConsole
from .context import SSHContext
from .exceptions import Goto, ProcessClosing, ProcessForciblyClosed
from .structs import Script


async def handle_client(proc: SSHServerProcess) -> None:
    """
    Factory method for handling client connections.

    Args:
        proc: The server process responsible for the client.
    """

    cx = await SSHContext._create(proc)

    if proc.subsystem:
        cx.log.error(f"Requested unimplemented subsystem: {proc.subsystem}")
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

    w, h, _, _ = proc.get_terminal_size()
    cx.env["COLUMNS"] = str(w)
    cx.env["LINES"] = str(h)
    await cx.user.update(last=datetime.utcnow()).apply()  # type: ignore

    async def input_loop():
        timeout = int(get_config("ssh.session.timeout", 120))

        while not proc.is_closing():
            try:
                if timeout > 0:
                    r = await wait_for(proc.stdin.read(1024), timeout)
                else:
                    r = await proc.stdin.read(1024)

                await cx.input.put(r)

            except IncompleteReadError:
                # process is likely closing
                break

            except ProcessForciblyClosed:
                break

            except TimeoutError:
                cx.log.warn("Timed out")
                cx.echo("\n\n[bright_white on red] TIMED OUT [/]\n\n")
                break

            except TerminalSizeChanged as sz:
                cx.env["COLUMNS"] = str(sz.width)
                cx.env["LINES"] = str(sz.height)
                cx.console.width = sz.width
                cx.console.height = sz.height
                cx.events.add(EventData("resize", (sz.width, sz.height)))

        # disable capture of mouse events
        cx.echo("\x1b[?1000l\x1b[?1003l\x1b[?1015l\x1b[?1006l")
        # show cursor
        cx.echo("\x1b[?25h")

        if proc.channel:
            proc.channel.close()

        proc.close()

    async def main_process():
        """Userland script stack; main process."""

        cx.console = XthuluConsole(
            encoding=cx.encoding,
            height=h,
            ssh_writer=proc.stdout,
            width=w,
            _environ=cx.env,
        )
        # prep script stack with top scripts;
        # since we're treating it as a stack and not a queue, add them
        # reversed so they are executed in the order they were defined
        top_names: list[str] = get_config("ssh.userland.top", ("top",))
        cx.stack = [Script(s, (), {}) for s in reversed(top_names)]

        # main script engine loop
        while len(cx.stack):
            current = cx.stack.pop()

            try:
                await cx.runscript(current)
            except Goto as goto_script:
                cx.stack = [goto_script.value]
            except ProcessClosing:
                cx.stack = []

        if proc.channel:
            cx.console.set_window_title("")
            proc.channel.close()

        proc.close()

    cx.log.info("Starting terminal session")

    try:
        await gather(input_loop(), main_process())
    except Exception:
        cx.log.exception("Exception in handler process")
    finally:
        if proc.channel:
            proc.channel.close()

        proc.close()
