"""New user application script"""

# 3rd party
from textual import events
from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.widgets import Button

# api
from xthulu.ssh.console.app import XthuluApp
from xthulu.ssh.context import SSHContext


class NuaApp(XthuluApp):
    """New user application"""

    CSS = """
        Button {
            margin-bottom: 1;
            width: 24;
        }
    """
    """Stylesheet"""

    def compose(self) -> ComposeResult:
        yield Center(
            Middle(
                Button("Continue as guest", variant="success", name="guest"),
                Button("Create an account", variant="primary", name="create"),
                Button("Log off", variant="error", name="logoff"),
            ),
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name == "guest":
            return self.exit(result="guest")

        if event.button.name == "logoff":
            return self.exit(result="logoff")

        self.exit(result="create")

    async def on_key(self, event: events.Key) -> None:
        if event.key != "escape":
            return

        self.exit(result="logoff")


async def main(cx: SSHContext) -> str:
    return await NuaApp(cx).run_async()  # type: ignore
