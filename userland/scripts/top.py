"""Userland entry point"""

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
        # if you don't use Textual apps, you can lift this restriction
        cx.echo(
            "[red]ERROR:[/] Unfortunately, only [bright_white]utf-8[/] "
            "encoding is currently supported\n"
        )
        return

    await cx.inkey(
        "You have to quit vim to proceed. Press a key when you're ready.",
        "dots8Bit",
    )
    await cx.redirect(["/usr/bin/vi", "-R", "/app/xthulu/ssh/server.py"])
    await scroll_art(cx, "userland/artwork/login.ans", "amiga")
    await cx.inkey("Press any key to continue", "arc")
    cx.echo(
        ":skull: [bold bright_green]x[/][green]thulu[/] ",
        "terminal server [italic]v1.0.0a0[/]\n",
        "[bright_black]https://github.com/haliphax/xthulu[/]\n\n",
    )

    bar_text = "".join(
        [
            "[bright_white]Connecting:[/] ",
            f"[bright_cyan underline]{cx.user.name}[/]",
            f"@[cyan]{cx.ip}[/]",
        ]
    )

    for _ in track(sequence=range(20), description=bar_text, console=cx.term):
        if await cx.inkey(timeout=0.1):
            break

    await cx.gosub("oneliners")
    await cx.gosub("lock_example")
