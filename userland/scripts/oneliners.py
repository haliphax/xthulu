"""Oneliners script"""

# 3rd party
import aiofiles as aiof
from textual import events
from textual.validation import Length
from textual.widgets import Input, Label, ListItem, ListView

# api
from xthulu.resources import Resources
from xthulu.ssh.console.app import XthuluApp
from xthulu.ssh.context import SSHContext

# local
from userland.models import Oneliner

LIMIT = 200
"""Total number of oneliners to load"""


class OnlinersApp(XthuluApp):
    artwork: str
    error_message: Label
    oneliners: list[Oneliner]

    def __init__(
        self,
        context: SSHContext,
        artwork: str,
        oneliners: list[Oneliner],
        **kwargs,
    ):
        self.artwork = artwork
        self.oneliners = oneliners
        super().__init__(context, **kwargs)

    def compose(self):
        input_widget = Input(
            placeholder="Enter a oneliner or press ESC",
            validators=Length(
                maximum=78,
                failure_description="Too long; must be <= 78 characters",
            ),
            validate_on=("submitted",),
        )
        input_widget.focus()
        self.error_message = Label(id="err")
        self.error_message.visible = False

        yield Label(self.artwork)
        yield ListView(*[ListItem(Label(o.message)) for o in self.oneliners])
        yield self.error_message
        yield input_widget

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.validation_result and not event.validation_result.is_valid:
            message = "".join(
                (
                    " ",
                    "... ".join(event.validation_result.failure_descriptions),
                )
            )
            self.error_message.update(message)
            self.error_message.visible = True
            return

        val = event.input.value.strip()

        if val != "":
            await Oneliner.create(message=val, user_id=self.context.user.id)

        self.exit()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.exit()


async def main(cx: SSHContext):
    db = Resources().db
    oneliners = [
        oneliner
        for oneliner in reversed(
            await db.all(
                Oneliner.query.order_by(Oneliner.id.desc()).limit(LIMIT)
            ),
        )
    ]

    async with aiof.open("userland/artwork/login.ans") as f:
        artwork = "\n".join(await f.readlines())

    app = OnlinersApp(cx, artwork, oneliners, css_path="oneliners.tcss")
    await app.run_async()
