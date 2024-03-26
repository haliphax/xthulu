"""Message viewer screen"""

# 3rd party
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, MarkdownViewer

# api
from xthulu.models import Message


class ViewScreen(Screen):

    """Message viewer screen"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", show=False),
    ]

    message: Message

    def __init__(self, *args, message: Message, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self):
        yield MarkdownViewer(
            markdown=self.message.content, show_table_of_contents=False
        )
        yield Footer()
