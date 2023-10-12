"""Oneliners script"""

# stdlib
from math import floor

# 3rd party
from rich.text import Text
from textual import events
from textual.validation import Length
from textual.widgets import Input, Label, ListItem, ListView

# api
from xthulu.resources import Resources
from xthulu.ssh.console.app import XthuluApp
from xthulu.ssh.console.art import load_art
from xthulu.ssh.context import SSHContext

# local
from userland.models import Oneliner

BANNER_PADDING = 10
"""Required space leftover to display banner art"""

LIMIT = 200
"""Total number of oneliners to load"""


class OnlinersApp(XthuluApp):
    CSS = """
        Label {
            width: 100%;
        }

        #err {
            background: #a00;
            color: #fff;
        }
    """

    # custom props
    artwork: list[str]
    banner: Label
    error_message: Label
    oneliners: list[Oneliner]

    def __init__(
        self,
        context: SSHContext,
        oneliners: list[Oneliner],
        artwork: list[str],
        **kwargs,
    ):
        self.artwork = artwork
        self.oneliners = oneliners
        super().__init__(context, **kwargs)

    def _update_banner(self):
        padded = []
        pad_left = " " * floor(self.context.term.width / 2 - 40)

        for line in self.artwork:
            padded += [pad_left, line]

        text = Text.from_ansi(
            "".join(padded), overflow="crop", no_wrap=True, end=""
        )
        self.banner.update(text)

    def compose(self):
        # banner
        self.banner = Label(markup=False)

        if self.console.height < len(self.artwork) + BANNER_PADDING:
            self.banner.display = False
        else:
            self._update_banner()

        yield self.banner

        # oneliners
        list = ListView(
            *[ListItem(Label(o.message)) for o in self.oneliners],
            initial_index=len(self.oneliners) - 1,
        )

        list.scroll_end(animate=False)
        yield list

        # error message
        self.error_message = Label(id="err")
        self.error_message.display = False
        yield self.error_message

        # input
        input_widget = Input(
            placeholder="Enter a oneliner or press ESC",
            validators=Length(
                maximum=Oneliner.MAX_LENGTH,
                failure_description=(
                    f"Too long; must be <= {Oneliner.MAX_LENGTH} characters"
                ),
            ),
            validate_on=(
                "changed",
                "submitted",
            ),
        )
        input_widget.focus()
        yield input_widget

    def on_input_changed(self, event: Input.Changed):
        if not event.validation_result or event.validation_result.is_valid:
            self.error_message.display = False
            return

        message = "".join(
            (
                " ",
                "... ".join(event.validation_result.failure_descriptions),
            )
        )
        self.error_message.update(message)
        self.error_message.display = True

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.validation_result and not event.validation_result.is_valid:
            return

        val = event.input.value.strip()

        if val != "":
            await Oneliner.create(message=val, user_id=self.context.user.id)

        self.exit()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.exit()

    def on_resize(self, event: events.Resize) -> None:
        if event.size.height < len(self.artwork) + BANNER_PADDING:
            self.banner.update("")
            self.banner.display = False
        else:
            self._update_banner()
            self.banner.display = True


async def main(cx: SSHContext):
    db = Resources().db
    oneliners: list[Oneliner] = [
        oneliner
        for oneliner in reversed(
            await db.all(
                Oneliner.query.order_by(Oneliner.id.desc()).limit(LIMIT)
            ),
        )
    ]

    artwork = await load_art("userland/artwork/oneliners.ans", "amiga")
    app = OnlinersApp(cx, oneliners, artwork)
    await app.run_async()
