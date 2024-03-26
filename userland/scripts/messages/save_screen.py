"""Save confirmation screen"""

# 3rd party
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label


class SaveScreen(ModalScreen):

    """Save confirmation screen"""

    CSS = """
        SaveScreen {
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

    response: str

    def compose(self):
        yield Vertical(
            Label("Do you want to save your message?"),
            Horizontal(
                Button("Save", variant="success", id="save"),
                Button("Continue", variant="primary", id="continue"),
                Button("Discard", variant="error", id="discard"),
            ),
            id="wrapper",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        assert event.button.id

        if event.button.id == "continue":
            self.app.pop_screen()  # pop this modal
            return

        if event.button.id == "save":
            # TODO save the message
            pass

        self.app.pop_screen()  # pop this modal
        self.app.pop_screen()  # pop the editor
