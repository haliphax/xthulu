"""Message details screen"""

# 3rd party
from sqlmodel import col, select
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual import validation
from textual.widgets import Button, Input, Label, TextArea

# api
from xthulu.resources import get_session
from xthulu.ssh.console.app import XthuluApp

# local
from userland.models import Message, MessageTag, MessageTags

MAX_TITLE_LENGTH = 120


class DetailsModal(ModalScreen):
    """Message details screen"""

    CSS = """
        DetailsModal {
            align: center middle;
            background: rgba(0, 0, 0, 0.5);
        }

        Label {
            margin-top: 1;
            width: 5;
        }

        Button {
            margin-top: 1;
            width: 50%;
        }

        Input {
            width: 53;
        }

        #save {
            margin-right: 1;
            margin-top: 1;
        }

        #wrapper {
            background: $primary-background;
            height: 12;
            padding: 1;
            width: 60;
        }
    """

    reply_to: Message | None
    response: str

    def __init__(self, *args, reply_to: Message | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.reply_to = reply_to

    def compose(self):
        yield Vertical(
            Horizontal(
                Label("Title", shrink=True),
                Input(
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
                ),
            ),
            Horizontal(
                Label("Tags", shrink=True),
                Input(id="tags"),
            ),
            Horizontal(
                Button("Save", variant="success", name="save", id="save"),
                Button("Cancel", variant="error", name="cancel"),
            ),
            id="wrapper",
        )

    async def on_mount(self) -> None:
        if not self.reply_to:
            return

        async with get_session() as db:
            tag_results = (
                await db.exec(
                    select(MessageTags).where(
                        MessageTags.message_id == self.reply_to.id
                    )
                )
            ).all()

        tags = " ".join([t.tag_name for t in tag_results])
        inp: Input = self.get_widget_by_id("tags")  # type: ignore
        inp.value = tags

    async def submit(self) -> None:
        app: XthuluApp = self.app  # type: ignore
        title: Input = self.get_widget_by_id("title")  # type: ignore
        title_validator = title.validate(title.value)

        if title_validator and not title_validator.is_valid:
            return

        content = self.app._background_screens[-1].query_one(TextArea)
        tags: Input = self.get_widget_by_id("tags")  # type: ignore
        tags_validator = tags.validate(tags.value)

        if tags_validator and not tags_validator.is_valid:
            return

        all_tags = set(tags.value.split(" "))

        async with get_session() as db:
            tag_results = (
                await db.exec(
                    select(MessageTag).where(col(MessageTag.name).in_(all_tags))
                )
            ).all()

        existing_tags = set([t.name for t in tag_results])
        nonexistent_tags = all_tags.difference(existing_tags)

        # create missing tags
        for t in nonexistent_tags:
            async with get_session() as db:
                db.add(MessageTag(name=t))
                await db.commit()

        # create message
        async with get_session() as db:
            message = Message(
                author_id=app.context.user.id,
                title=title.value,
                content=content.text,
                parent_id=self.reply_to.id if self.reply_to else None,
            )
            db.add(message)
            await db.commit()
            await db.refresh(message)
            assert message.id

        # link tags to message
        for t in all_tags:
            async with get_session() as db:
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

    async def key_escape(self, _):
        self.app.pop_screen()  # pop this modal
