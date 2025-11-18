"""Message viewer screen"""

# stdlib
from typing import Sequence

# 3rd party
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label, MarkdownViewer

# local
from userland.models import Message


class ViewScreen(Screen):
    """Message viewer screen"""

    BINDINGS = [
        ("escape", "app.pop_screen", "Exit"),
        Binding("f", "", show=False),
    ]

    CSS = """
        Horizontal Label {
            width: 50%;
        }

        Label {
            margin: 0;
        }

        MarkdownViewer {
            padding-top: 1;
        }

        #header {
            background: #007 100%;
            color: #fff;
            height: 5;
            padding-left: 1;
            padding-right: 1;
            padding-top: 1;
        }

        #title {
            width: auto;
            margin-bottom: 1;
        }
    """

    message: Message
    tags: Sequence[str]

    def __init__(self, *args, message: Message, tags: Sequence[str], **kwargs):
        super(ViewScreen, self).__init__(*args, **kwargs)
        self.message = message
        self.tags = tags

    def compose(self) -> ComposeResult:
        assert self.message.author

        with Vertical():
            with Vertical(id="header"):
                with Horizontal():
                    yield Label(
                        "[bold underline ansi_cyan]Author:[/]    "
                        f"{self.message.author.name}"
                    )
                    yield Label(
                        "[bold underline ansi_cyan]Posted:[/] "
                        f"{self.message.created.strftime('%H:%M %a %b %d %Y')}"
                    )

                with Horizontal():
                    yield Label(
                        "[bold underline ansi_cyan]Recipient:[/] "
                        f"{self.message.recipient.name if self.message.recipient else '<N/A>'}"
                    )
                    yield Label(
                        f"[bold underline ansi_cyan]Tags:[/]   "
                        f"{', '.join(self.tags)}"
                    )

                yield Label(
                    f"[bold underline ansi_cyan]Title:[/]     "
                    f"{self.message.title}",
                    id="title",
                )

            yield MarkdownViewer(
                markdown=self.message.content,
                show_table_of_contents=False,
            )
            yield Footer()
