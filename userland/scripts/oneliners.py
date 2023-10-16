"""Oneliners script"""

# 3rd party
from textual.validation import Length
from textual.widgets import Input, Label, ListItem, ListView

# api
from xthulu.resources import Resources
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.console.art import load_art
from xthulu.ssh.context import SSHContext

# local
from userland.models import Oneliner

LIMIT = 200
"""Total number of oneliners to load"""


class OnlinersApp(BannerApp):

    """Oneliners Textual app"""

    CSS = """
        $accent: ansi_red;
        $error: ansi_bright_red;

        Label {
            width: 100%;
        }

        ListItem {
            background: $primary-background;
        }

        ListItem.even {
            background: $secondary-background;
        }

        ListItem.--highlight {
            background: $accent;
        }

        #err {
            background: $error;
            color: black;
        }
    """
    """Stylesheet"""

    error_message: Label
    """Error message widget"""

    oneliners: list[Oneliner]
    """List of pre-loaded oneliner messages"""

    def __init__(
        self,
        context: SSHContext,
        artwork: list[str],
        oneliners: list[Oneliner],
        **kwargs,
    ):
        self.oneliners = oneliners
        super().__init__(context, artwork, **kwargs)
        self.bind("escape", "quit")

    def compose(self):
        for widget in super().compose():
            yield widget

        # oneliners
        list = ListView(
            *[
                ListItem(Label(o.message), classes="even" if idx % 2 else "")
                for idx, o in enumerate(self.oneliners)
            ],
            initial_index=len(self.oneliners) - 1,
        )
        list.styles.scrollbar_background = "black"
        list.styles.scrollbar_color = "ansi_yellow"
        list.styles.scrollbar_color_active = "white"
        list.styles.scrollbar_color_hover = "ansi_bright_yellow"

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


async def main(cx: SSHContext):
    cx.term.set_window_title("oneliners")
    db = Resources().db
    recent = (
        Oneliner.select("id")
        .order_by(Oneliner.id.desc())
        .limit(LIMIT)
        .alias("recent")
        .select()
    )
    oneliners: list[Oneliner] = await db.all(
        Oneliner.query.where(Oneliner.id.in_(recent))
    )

    artwork = await load_art("userland/artwork/oneliners.ans", "amiga")
    app = OnlinersApp(cx, artwork, oneliners)
    await app.run_async()
