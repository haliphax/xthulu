"""Message compose/reply screen"""

# 3rd party
from textual.screen import ModalScreen
from textual.widgets import TextArea

# local
from .save_screen import SaveScreen


class EditorScreen(ModalScreen):

    """Message compose/reply screen"""

    _content: str

    def __init__(self, *args, content="", **kwargs):
        self._content = content
        super().__init__(*args, **kwargs)

    def compose(self):
        yield TextArea(self._content)

    async def key_escape(self):
        await self.app.push_screen(SaveScreen())
