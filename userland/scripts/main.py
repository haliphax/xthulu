"""Main menu script"""

# 3rd party
from textual.app import ComposeResult
from textual.containers import Center, Middle, VerticalScroll
from textual.widgets import Button

# api
from xthulu.ssh.console.app import XthuluApp
from xthulu.ssh.context import SSHContext


class MenuApp(XthuluApp):
    """Main menu"""

    CSS = """
        Button {
            margin-bottom: 1;
            max-width: 100%;
            width: 20;
        }

        VerticalScroll {
            height: auto;
            width: 20;
        }
    """
    """Stylesheet"""

    def compose(self) -> ComposeResult:
        yield Center(
            Middle(
                VerticalScroll(
                    Button("Messages", name="messages"),
                    Button("Node chat", name="chat"),
                    Button("Oneliners", name="oneliners"),
                    Button("Lock example", name="lock_example"),
                    Button("Log off", name="goto_logoff", variant="error"),
                )
            )
        )
        # disable alternate buffer for main menu
        self.context.proc.stdout.write(b"\x1b[?1049l")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        assert event.button.name

        return self.exit(result=event.button.name)


async def main(cx: SSHContext) -> None:
    while True:
        cx.console.set_window_title("main menu")
        result: str | None = await MenuApp(cx).run_async()

        if not result:
            return

        if result.startswith("goto_"):
            cx.console.clear()
            return cx.goto(result[5:])

        await cx.gosub(result)
