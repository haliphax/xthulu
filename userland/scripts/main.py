"""Main menu script"""

# stdlib
from os import path

# 3rd party
from textual.app import ComposeResult
from textual.containers import Center, VerticalScroll
from textual.widgets import Button

# api
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext


class MenuApp(BannerApp[str]):
    """Main menu"""

    _last: str | None = None

    BANNER_PADDING = 8
    BINDINGS = [("escape", "quit", "Log off")]
    CSS = """
        Button {
            height: 5;
            width: 100%;
        }

        VerticalScroll {
            width: 100%;
        }

        #buttons {
            layout: grid;
            grid-gutter: 1 2;
            grid-size: 3;
            max-width: 80;
        }
    """
    """Stylesheet"""

    def __init__(self, context: SSHContext, last: str | None = None, **kwargs):
        super(MenuApp, self).__init__(context, **kwargs)
        self._last = last

    def compose(self) -> ComposeResult:
        # disable alternate buffer for main menu
        self.context.proc.stdout.write(b"\x1b[?1049l")

        for widget in super(MenuApp, self).compose():
            yield widget

        with VerticalScroll():
            with Center():
                with Center(id="buttons"):
                    yield Button("Messages", id="messages")
                    yield Button("Node chat", id="chat")
                    yield Button("Oneliners", id="oneliners")
                    yield Button("Lock example", id="lock_example")
                    yield Button("Log off", id="goto_logoff", variant="error")

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
