"""Message compose/reply screen"""

# 3rd party
from textual.screen import ModalScreen
from textual.widgets import TextArea

# local
from userland.models.message import Message
from .save_modal import SaveModal


class EditorScreen(ModalScreen):

    """Message compose/reply screen"""

    _content: str
    reply_to: Message | None

    def __init__(
        self, *args, content="", reply_to: Message | None = None, **kwargs
    ):
        self._content = content
        self.reply_to = reply_to
        super().__init__(*args, **kwargs)

    def compose(self):
        yield TextArea(self._content)

    async def key_escape(self):
        await self.app.push_screen(SaveModal(reply_to=self.reply_to))
