"""Message details screen"""

# stdlib
from typing import Sequence

# 3rd party
from sqlmodel import and_, col, func, select
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual import validation
from textual.widgets import Button, Input, Label, SelectionList, TextArea
from textual.widgets.selection_list import Selection

# api
from xthulu.models import User
from xthulu.resources import db_session
from xthulu.ssh.console.app import XthuluApp

# local
from userland.models import Message, MessageTag, MessageTags

MAX_TITLE_LENGTH = 120


class DetailsModal(ModalScreen):
    """Message details screen"""

    BINDINGS = [("escape", "app.pop_screen", "")]
    CSS = """
        DetailsModal {
            align: center middle;
            background: rgba(0, 0, 0, 0.5);
        }

        Label {
            margin-top: 1;
            width: 5
        }

        Input {
            width: 53;
        }

        SelectionList {
            height: 10;
        }

        Button {
            margin-top: 1;
            width: 50%;
        }

        #save {
            margin-right: 1;
            margin-top: 1;
        }

        #wrapper {
            background: $primary-background;
            height: 23;
            padding: 1;
            width: 60;
        }
    """

    reply_to: Message | None
    response: str

    def __init__(self, *args, reply_to: Message | None = None, **kwargs):
        super(DetailsModal, self).__init__(*args, **kwargs)
        self.reply_to = reply_to

    def compose(self):
        with Vertical():
            with Horizontal():
                yield Label("Title", shrink=True)
                yield Input(
                    (
                        f"Re: {self.reply_to.title.lstrip('Re: ')}"
                        if self.reply_to
                        else ""
                    ),
                    id="title",
                    max_length=MAX_TITLE_LENGTH,
                    validators=[
                        validation.Length(
                            1, failure_description="Title is required"
                        )
                    ],
                    validate_on=("changed", "submitted"),
                )

            with Horizontal():
                yield Label("To", shrink=True)
                yield Input(
                    id="to",
                    max_length=User.MAX_NAME_LENGTH,
                )

            yield SelectionList(id="tags")

            with Horizontal(id="wrapper"):
                yield Button("Save", variant="success", name="save", id="save")
                yield Button("Cancel", variant="error", name="cancel")

    async def on_mount(self) -> None:
        tags: SelectionList = self.get_widget_by_id("tags")  # type: ignore

        async with db_session() as db:
            if not self.reply_to:
                my_recipient = None
                my_tags = []
            else:
                my_recipient = (
                    await db.exec(
                        select(User).where(User.id == self.reply_to.author_id)
                    )
                ).one_or_none()
                my_tags = (
                    await db.exec(
                        select(MessageTags.tag_name).where(
                            MessageTags.message_id == self.reply_to.id
                        )
                    )
                ).all()

            to: Input = self.get_widget_by_id("to")  # type: ignore
            to.value = my_recipient.name if my_recipient else ""
            all_tags: Sequence[str] = (  # type: ignore
                await db.exec(
                    select(MessageTag.name).where(
                        and_(
                            col(MessageTag.name).is_not(None),
                            col(MessageTag.name).not_in(my_tags),
                        )
                    )
                )
            ).all()

        tags.add_options([Selection(t, t, True) for t in my_tags])
        tags.add_options([Selection(t, t, False) for t in all_tags])

    async def submit(self) -> None:
        app: XthuluApp = self.app  # type: ignore
        title: Input = self.get_widget_by_id("title")  # type: ignore
        title_validator = title.validate(title.value)

        if title_validator and not title_validator.is_valid:
            return

        content = self.app._background_screens[-1].query_one(TextArea)
        to: Input = self.get_widget_by_id("to")  # type: ignore
        tags: SelectionList = self.get_widget_by_id("tags")  # type: ignore

        if len(tags.selected) == 0:
            return

        async with db_session() as db:
            recipient: User | None = None

            # validate recipient
            if to.value != "":
                recipient = (
                    await db.exec(
                        select(User).where(
                            func.lower(User.name) == to.value.lower()
                        )
                    )
                ).one_or_none()

                if recipient is None:
                    to.value = "No such user!"
                    return

            # create message
            message = Message(
                author_id=app.context.user.id,
                title=title.value,
                content=content.text,
                recipient=recipient,
                parent_id=self.reply_to.id if self.reply_to else None,
            )
            db.add(message)
            await db.commit()
            await db.refresh(message)
            assert message.id

        # link tags to message
        for t in tags.selected:
            async with db_session() as db:
                db.add(MessageTags(message_id=message.id, tag_name=t))
                await db.commit()

        self.app.pop_screen()  # pop this modal
        self.app.pop_screen()  # pop the editor

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self.submit()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name == "cancel":
            self.app.pop_screen()  # pop this modal
            return

        await self.submit()
