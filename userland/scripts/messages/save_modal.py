"""Save confirmation screen"""

# 3rd party
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

# local
from userland.models import Message
from .details_modal import DetailsModal


class SaveModal(ModalScreen):
    """Save confirmation screen"""

    BINDINGS = [("escape", "app.pop_screen", "")]

    CSS = """
        SaveModal {
            align: center middle;
            background: rgba(0, 0, 0, 0.5);
        }

        Button {
            margin: 1;
            width: 33%;
        }

        #save {
            margin-left: 0;
            margin-top: 1;
        }

        #wrapper {
            background: $primary-background;
            height: 7;
            padding: 1;
            width: 60;
        }
    """

    reply_to: Message | None

    def __init__(self, *args, reply_to: Message | None = None, **kwargs):
        super(SaveModal, self).__init__(*args, **kwargs)
        self.reply_to = reply_to

    def compose(self):
        with Vertical(id="wrapper"):
            yield Label("Do you want to save your message?")

            with Horizontal():
                yield Button("Save", variant="success", id="save")
                yield Button("Continue", variant="primary", id="continue")
                yield Button("Discard", variant="error", id="discard")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        assert event.button.id

        if event.button.id == "continue":
            self.app.pop_screen()  # pop this modal
            return

        if event.button.id == "save":
            self.app.pop_screen()
            await self.app.push_screen(DetailsModal(reply_to=self.reply_to))
            return

        self.app.pop_screen()  # pop this modal
        self.app.pop_screen()  # pop the editor
