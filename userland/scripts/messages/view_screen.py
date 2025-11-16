"""Message viewer screen"""

# stdlib
from typing import Sequence

# 3rd party
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label, MarkdownViewer

# local
from userland.models import Message


class ViewScreen(Screen):
    """Message viewer screen"""

    BINDINGS = [("escape", "app.pop_screen", "Exit")]
    CSS = """
        Label {
            width: 50%;
        }

        MarkdownViewer {
            padding-top: 1;
        }

        #header {
            background: #700;
            height: 4;
            padding-left: 1;
            padding-right: 1;
            padding-top: 1;
        }
    """

    message: Message
    tags: Sequence[str]

    def __init__(self, *args, message: Message, tags: Sequence[str], **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.tags = tags

    def compose(self):
        assert self.message.author
        yield Vertical(
            Vertical(
                Horizontal(
                    Label(
                        f"[bold underline]Author:[/] {self.message.author.name}"
                    ),
                    Label(
                        f"[bold underline]Posted:[/] {self.message.created.strftime('%H:%M %a %b %d %Y')}"
                    ),
                ),
                Horizontal(
                    Label(f"[bold underline]Title:[/]  {self.message.title}"),
                    Label(f"[bold underline]Tags:[/]   {', '.join(self.tags)}"),
                ),
                id="header",
            ),
            MarkdownViewer(
                markdown=self.message.content,
                show_table_of_contents=False,
            ),
            Footer(),
        )
