"""New user application script"""

# stdlib
from os import path

# 3rd party
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.widgets import Button

# api
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext


class NuaApp(BannerApp[str]):
    """New user application"""

    BANNER_PADDING = 2
    CSS_PATH = path.join(path.dirname(__file__), "nua.tcss")

    def compose(self) -> ComposeResult:
        for widget in super(NuaApp, self).compose():
            yield widget

        with Center():
            with Horizontal(id="buttons_wrapper"):
                yield Button(
                    "Continue as guest",
                    flat=True,
                    variant="success",
                    id="guest",
                )
                yield Button(
                    "Create an account",
                    flat=True,
                    variant="primary",
                    id="create",
                )
                yield Button(
                    "Log off",
                    flat=True,
                    variant="error",
                    id="logoff",
                )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(result=event.button.id)

    async def on_key(self, event: events.Key) -> None:
        if event.key != "escape":
            return

        self.exit(result="logoff")


async def main(cx: SSHContext) -> str | None:
    cx.console.set_window_title("new user application")
    return await NuaApp(
        cx,
        art_path=path.join("userland", "artwork", "nua.ans"),
        art_encoding="amiga",
        alt="79 Columns // New user application",
    ).run_async()
