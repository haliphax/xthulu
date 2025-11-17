"""Userland entry point"""

# stdlib
from importlib.metadata import version
from os import path

# 3rd party
from rich.progress import track

# api
from xthulu.ssh.console.art import scroll_art
from xthulu.ssh.console.choice import choice
from xthulu.ssh.console.internal.file_wrapper import FileWrapper
from xthulu.ssh.context import SSHContext


async def main(cx: SSHContext) -> None:
    if cx.encoding == "utf-8":
        cx.echo("\x1b%G")
    elif cx.env["TERM"] != "ansi":
        cx.echo("\x1b%@\x1b(U")

    if cx.encoding != "utf-8":
        cx.echo(
            "[red]ERROR:[/] Unfortunately, only [bright_white]utf-8[/] "
            "encoding is currently supported. Encoding will be forced if "
            "you proceed.\n"
        )

        if not await cx.inkey("Press any key to continue", timeout=30):
            return

        cx.console._encoding = "utf-8"
        f: FileWrapper = cx.console._file  # type: ignore
        f._encoding = "utf-8"
        cx.encoding = "utf-8"

    cx.console.set_window_title(f"{cx.username}@79columns")
    await scroll_art(cx, path.join("userland", "artwork", "login.ans"), "cp437")
    await cx.inkey("Press any key to continue", "dots8Bit", timeout=5)

    # new user application
    if cx.username == "guest":
        result = await cx.gosub("nua")

        if result == "create":
            cx.echo("Yeah, only that's not ready yet.\n\n")
            return

        if not result or result == "logoff":
            return

    if await choice(cx, "Skip to main menu? ", ("No", "Yes")) == "Yes":
        cx.console.clear()
        cx.goto("main")
        return

    cx.echo("\n")
    cx.console.set_window_title("system information")
    await scroll_art(
        cx, path.join("userland", "artwork", "sysinfo.ans"), "amiga"
    )
    cx.echo(
        ":skull: [bold bright_green]x[/][green]thulu[/] ",
        f"terminal server [italic]v{version('xthulu')}[/]\n",
        "[bright_black]https://github.com/haliphax/xthulu[/]\n\n",
    )
    # alpine only?
    await cx.redirect(["/bin/ash", "-c", "uname -a; echo -e '\\r'; sleep 0.1"])
    await cx.inkey("Press any key to continue", "arc")

    cx.console.set_window_title("logging in...")
    bar_text = "".join(
        [
            "[bright_white]Connecting:[/] ",
            f"[bright_cyan underline]{cx.user.name}[/]",
            f"@[cyan]{cx.ip}[/]",
        ]
    )

    waiting = True

    for _ in track(
        sequence=range(20), description=bar_text, console=cx.console
    ):
        if waiting and await cx.inkey(timeout=0.1):
            waiting = False

    await cx.inkey(timeout=0.1)  # show bar at 100% before switching screens
    await cx.gosub("oneliners")
    cx.console.clear()
    cx.goto("main")
