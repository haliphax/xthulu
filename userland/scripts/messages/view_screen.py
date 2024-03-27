"""Message viewer screen"""

# 3rd party
from textual.screen import Screen
from textual.widgets import Footer, MarkdownViewer

# local
from userland.models import Message


class ViewScreen(Screen):
    """Message viewer screen"""

    BINDINGS = [("escape", "app.pop_screen", "Exit")]

    message: Message

    def __init__(self, *args, message: Message, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    def compose(self):
        yield MarkdownViewer(
            markdown=self.message.content, show_table_of_contents=False
        )
        yield Footer()
