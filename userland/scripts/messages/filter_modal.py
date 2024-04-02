"""Filter messages screen"""

# 3rd party
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label


class FilterModal(ModalScreen[list[str]]):
    """Filter messages screen"""

    CSS = """
        FilterModal {
            align: center middle;
            background: rgba(0, 0, 0, 0.5);
        }

        Button {
            margin: 1;
            width: 50%;
        }

        Label {
            margin-top: 1;
        }

        Input {
            width: 54;
        }

        #filter {
            margin-left: 0;
            margin-top: 1;
        }

        #wrapper {
            background: $primary-background;
            height: 9;
            padding: 1;
            width: 60;
        }
    """

    _tags: list[str]

    def __init__(self, *args, tags: list[str] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._tags = tags or []

    def compose(self):
        yield Vertical(
            Horizontal(
                Label("Tags"),
                Input(" ".join(self._tags)),
            ),
            Horizontal(
                Button("Filter", variant="success", id="filter", name="filter"),
                Button("Cancel", variant="error", id="cancel", name="cancel"),
            ),
            id="wrapper",
        )

    def _submit(self) -> None:
        tags = self.query_one(Input)
        assert tags
        self.dismiss(tags.value.split(" "))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name == "cancel":
            self.app.pop_screen()  # pop this modal
            return

        self._submit()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit()

    async def key_escape(self, _):
        self.app.pop_screen()  # pop this modal
