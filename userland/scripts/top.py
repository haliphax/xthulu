"""Userland entry point"""

# stdlib
from asyncio import sleep

# 3rd party
from rich.progress import track
from textual.app import ComposeResult
from textual.widgets import Welcome

# api
from xthulu.ssh.console.app import XthuluApp
from xthulu.ssh.context import SSHContext
from xthulu.logger import log


class WelcomeApp(XthuluApp):
    def compose(self) -> ComposeResult:
        yield Welcome()

    def on_button_pressed(self) -> None:
        log.info("pressed")
        self.exit()


async def main(cx: SSHContext):
    if cx.encoding == "utf-8":
        cx.echo("\x1b%G")
    elif cx.env["TERM"] != "ansi":
        cx.echo("\x1b%@\x1b(U")

    cx.echo(
        "\n",
        "💀 " if cx.encoding == "utf-8" else "",
        "[bold bright_green]x[/][green]thulu[/] ",
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

    for _ in track(range(20), description=bar_text, console=cx.term):
        await sleep(0.1)

    await cx.gosub("oneliners")
    await cx.gosub("lock_example")

    app = WelcomeApp(context=cx)
    await app.run_async()

    cx.echo("\n\nGoodbye, then!\n\n")
