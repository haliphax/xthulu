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


class NuaApp(BannerApp):
    """New user application"""

    CSS = """
        Button {
            width: 21;
        }
        Center {
            height: 5;
        }
        Horizontal {
            width: 65;
        }
        #create, #guest {
            margin-right: 1;
        }
    """
    """Stylesheet"""

    def compose(self) -> ComposeResult:
        for widget in super().compose():
            yield widget

        yield Center(
            Horizontal(
                Button(
                    "Continue as guest",
                    variant="success",
                    id="guest",
                ),
                Button(
                    "Create an account",
                    variant="primary",
                    id="create",
                ),
                Button("Log off", variant="error", id="logoff"),
            )
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
    ).run_async()
