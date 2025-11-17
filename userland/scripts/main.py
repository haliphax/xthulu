"""Main menu script"""

# stdlib
from os import path

# 3rd party
from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.widgets import Button

# api
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext


class MenuApp(BannerApp[str]):
    """Main menu"""

    BINDINGS = [("escape", "quit", "Log off")]
    CSS = """
        Button {
            height: 5;
            width: 100%;
        }

        #wrapper {
            overflow-x: auto;
            overflow-y: auto;
        }

        #buttons {
            layout: grid;
            grid-gutter: 1 2;
            grid-size: 3;
            max-width: 80;
        }
    """
    """Stylesheet"""
    _last: str | None = None

    def __init__(self, context: SSHContext, last: str | None = None, **kwargs):
        super(MenuApp, self).__init__(context, **kwargs)
        self._last = last

    def compose(self) -> ComposeResult:
        self.context.console.clear()

        for widget in super(MenuApp, self).compose():
            yield widget

        yield Vertical(
            Center(
                Center(
                    Button("Messages", id="messages"),
                    Button("Node chat", id="chat"),
                    Button("Oneliners", id="oneliners"),
                    Button("Lock example", id="lock_example"),
                    Button("Log off", id="goto_logoff", variant="error"),
                    id="buttons",
                ),
                id="wrapper",
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
        self.set_focus(None)

        if self._last:
            btn = self.get_widget_by_id(self._last)
            btn.focus()


async def main(cx: SSHContext) -> None:
    result: str | None = None

    while True:
        cx.console.set_window_title("main menu")
        result = await MenuApp(
            cx,
            result,
            art_path=path.join("userland", "artwork", "main.ans"),
            art_encoding="amiga",
            alt="79 Columns // Main menu",
        ).run_async()

        if not result:
            result = "goto_logoff"

        if result.startswith("goto_"):
            break

        await cx.gosub(result)

    cx.console.clear()
    cx.goto(result[5:])
