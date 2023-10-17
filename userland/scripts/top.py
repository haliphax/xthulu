"""Userland entry point"""

# stdlib
from importlib.metadata import version

# 3rd party
from rich.progress import track

# api
from xthulu.ssh.console.art import scroll_art
from xthulu.ssh.context import SSHContext


async def main(cx: SSHContext):
    if cx.encoding == "utf-8":
        cx.echo("\x1b%G")
    elif cx.env["TERM"] != "ansi":
        cx.echo("\x1b%@\x1b(U")

    if cx.encoding != "utf-8":
        # if you don't use Textual apps, you can lift this restriction
        cx.echo(
            "[red]ERROR:[/] Unfortunately, only [bright_white]utf-8[/] "
            "encoding is currently supported\n"
        )
        return

    cx.goto("chat")
    cx.console.set_window_title(f"{cx.username}@79columns")
    await scroll_art(cx, "userland/artwork/login.ans", "cp437")
    await cx.inkey("Press any key to continue", "dots8Bit")

    cx.console.set_window_title("system information")
    await scroll_art(cx, "userland/artwork/sysinfo.ans", "amiga")
    cx.echo(
        ":skull: [bold bright_green]x[/][green]thulu[/] ",
        f"terminal server [italic]v{version('xthulu')}[/]\n",
        "[bright_black]https://github.com/haliphax/xthulu[/]\n\n",
    )
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

    await cx.gosub("oneliners")
    await cx.gosub("messages")
    await cx.gosub("chat")
