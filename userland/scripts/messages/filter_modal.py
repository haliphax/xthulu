"""Filter messages screen"""

# stdlib
from typing import Sequence

# 3rd party
from sqlmodel import and_, col, select
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, SelectionList
from textual.widgets.selection_list import Selection

# api
from xthulu.resources import db_session

# local
from userland.models.message.tag import MessageTag


class FilterModal(ModalScreen[list[str]]):
    """Filter messages screen"""

    BINDINGS = [("escape", "app.pop_screen", "")]
    CSS = """
        FilterModal {
            align: center middle;
            background: rgba(0, 0, 0, 0.5);
        }

        Button {
            margin: 1;
            width: 33.3333%;
        }

        SelectionList {
            height: 10;
        }

        #filter {
            margin-left: 0;
            margin-top: 1;
        }

        #wrapper {
            background: $primary-background;
            height: 16;
            padding: 1;
            width: 60;
        }
    """

    _tags: list[str]

    def __init__(self, *args, tags: list[str] | None = None, **kwargs):
        super(FilterModal, self).__init__(*args, **kwargs)
        self._tags = tags or []

    def compose(self):
        yield Vertical(
            SelectionList(id="tags"),
            Horizontal(
                Button("Filter", variant="success", id="filter"),
                Button("Reset", id="reset"),
                Button("Cancel", variant="error", id="cancel"),
            ),
            id="wrapper",
        )

    def _submit(self) -> None:
        tags = self.query_one(SelectionList)
        assert tags
        self.dismiss(tags.selected)

    async def on_mount(self) -> None:
        tags = self.query_one(SelectionList)
        assert tags
        tags.add_options([Selection(t, t, True) for t in self._tags])

        async with db_session() as db:
            all_tags: Sequence[str] = (  # type: ignore
                await db.exec(
                    select(MessageTag.name).where(
                        and_(
                            col(MessageTag.name).is_not(None),
                            col(MessageTag.name).not_in(self._tags),
                        )
                    )
                )
            ).all()

        tags.add_options([Selection(t, t, False) for t in all_tags])

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()  # pop this modal
            return

        if event.button.id == "reset":
            self.dismiss([])
            return

        self._submit()
