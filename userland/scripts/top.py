"""Userland entry point"""

# api
from xthulu.ssh.context import SSHContext
from xthulu.ssh.ui import show_art


async def main(cx: SSHContext):
    if cx.encoding == "utf-8":
        cx.echo("\x1b%G")
    elif cx.env["TERM"] != "ansi":
        cx.echo("\x1b%@\x1b(U")

    cx.echo(
        f"{cx.term.normal}\r\nConnected: "
        f"{cx.term.bold_blue(cx.user.name)}@"
        f"{cx.term.bold_blue(cx.ip)}\r\n"
    )

    await show_art(cx, "userland/artwork/login.ans")
    await cx.gosub("oneliners")
