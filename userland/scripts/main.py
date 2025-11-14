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

    BINDINGS = [("escape", "quit", "Log off")]
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
    _last: str | None = None

    def __init__(self, context: SSHContext, last: str | None = None, **kwargs):
        super().__init__(context, **kwargs)
        self._last = last

    def compose(self) -> ComposeResult:
        yield Center(
            Middle(
                VerticalScroll(
                    Button("Messages", id="messages"),
                    Button("Node chat", id="chat"),
                    Button("Oneliners", id="oneliners"),
                    Button("Lock example", id="lock_example"),
                    Button("Log off", id="goto_logoff", variant="error"),
                )
            )
        )
        # disable alternate buffer for main menu
        self.context.proc.stdout.write(b"\x1b[?1049l")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        assert event.button.id
        return self.exit(result=event.button.id)

    async def action_quit(self) -> None:
        self.context.console.clear()
        self.context.goto("logoff")

    async def on_ready(self) -> None:
        if self._last:
            btn = self.get_widget_by_id(self._last)
            btn.focus()


async def main(cx: SSHContext) -> None:
    result: str | None = None

    while True:
        cx.console.set_window_title("main menu")
        result = await MenuApp(cx, result).run_async()

        if not result:
            result = "goto_logoff"

        if result.startswith("goto_"):
            cx.console.clear()
            return cx.goto(result[5:])

        await cx.gosub(result)
