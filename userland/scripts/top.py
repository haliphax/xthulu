"""Userland entry point"""

# stdlib
from asyncio import sleep

# api
from xthulu.ssh.context import SSHContext
from xthulu.ssh.ui import show_art


async def main(cx: SSHContext):
    if cx.encoding == "utf-8":
        cx.echo("\x1b%G")
    elif cx.env["TERM"] != "ansi":
        cx.echo("\x1b%@\x1b(U")

    cx.echo(
        cx.term.normal,
        "\r\n",
        "💀 " if cx.encoding == "utf-8" else "",
        cx.term.bold_green("x"),
        cx.term.green("thulu"),
        " terminal server ",
        cx.term.italic("v1.0.0a0"),
        "\r\n",
        cx.term.bold_black("https://github.com/haliphax/xthulu"),
        "\r\n\r\n",
        cx.term.bold_white("Connecting: "),
        cx.term.bold_cyan_underline(cx.user.name),
        "@",
        cx.term.cyan(cx.ip),
        " ",
    )

    for color in ("bold_black", "white", "bold_white"):
        colorfunc = getattr(cx.term, color)
        await sleep(0.5)
        cx.echo(colorfunc("."))

    await sleep(0.5)
    cx.echo(f"{cx.term.normal}\r\n")
    await show_art(cx, "userland/artwork/login.ans")

    await cx.gosub("oneliners")
    await cx.gosub("lock_example")
    await cx.gosub("editor_demo")
