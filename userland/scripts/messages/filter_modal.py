"""Filter messages screen"""

# 3rd party
from sqlmodel import select
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, OptionList
from textual.widgets.option_list import Option

# api
from xthulu.resources import db_session

# local
from userland.models.message.tag import MessageTag


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

        #autocomplete_wrapper {
            height: 5;
        }

        #filter {
            margin-left: 0;
            margin-top: 1;
        }

        #wrapper {
            background: $primary-background;
            height: 15;
            padding: 1;
            width: 60;
        }
    """

    _tags: list[str]
    _alltags: list[str] = []

    def __init__(self, *args, tags: list[str] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._tags = tags or []

    def compose(self):
        yield Vertical(
            Horizontal(
                Label("Tags"),
                Input(" ".join(self._tags)),
            ),
            Horizontal(OptionList(disabled=True), id="autocomplete_wrapper"),
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

    async def on_mount(self) -> None:
        async with db_session() as db:
            tags_result = (await db.exec(select(MessageTag))).all()

        self._alltags = [t.name for t in tags_result]  # type: ignore

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name == "cancel":
            self.app.pop_screen()  # pop this modal
            return

        self._submit()

    async def on_input_changed(self, event: Input.Changed) -> None:
        last_word = event.input.value.split(" ")[-1]
        selections = self.query_one(OptionList)
        selections.clear_options()

        if last_word == "":
            selections.disabled = True
            return

        suggestions = [
            Option(t) for t in self._alltags if t.startswith(last_word)
        ]
        selections.disabled = False
        selections.add_options(suggestions)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self._submit()

    async def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        tags_input = self.query_one(Input)
        tags = tags_input.value.split(" ")[:-1]
        tags.append(str(event.option.prompt))
        tags_input.value = "".join([" ".join(tags), " "])
        tags_input.focus()
        event.option_list.clear_options()
        event.option_list.disabled = True

    async def key_escape(self, _):
        self.app.pop_screen()  # pop this modal
