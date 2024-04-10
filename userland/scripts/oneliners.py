"""Oneliners script"""

# stdlib
from os import path

# 3rd party
from textual.widgets import Input, Label, ListItem, ListView

# api
from xthulu.resources import Resources
from xthulu.ssh.console.banner_app import BannerApp
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

        ListView:focus ListItem.--highlight {
            background: $accent;
        }

        #err {
            background: $error;
            color: black;
        }
    """
    """Stylesheet"""

    def __init__(self, context: SSHContext, **kwargs):
        super().__init__(context, **kwargs)
        self.bind("escape", "quit")

    def compose(self):
        for widget in super().compose():
            yield widget

        # oneliners
        lv = ListView()
        lv.styles.scrollbar_background = "black"
        lv.styles.scrollbar_color = "ansi_yellow"
        lv.styles.scrollbar_color_active = "white"
        lv.styles.scrollbar_color_hover = "ansi_bright_yellow"
        yield lv

        # error message
        err = Label(id="err")
        err.display = False
        yield err

        # input
        input_widget = Input(
            max_length=Oneliner.MAX_LENGTH,
            placeholder="Enter a oneliner or press ESC",
        )
        input_widget.focus()
        yield input_widget

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.input.value.strip()

        if val != "":
            await Oneliner.create(message=val, user_id=self.context.user.id)

        self.exit()

    async def on_mount(self) -> None:
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
        lv = self.query_one(ListView)

        for idx, o in enumerate(oneliners):
            lv.mount(
                ListItem(Label(o.message), classes="even" if idx % 2 else "")
            )

        lv.index = len(oneliners) - 1
        lv.scroll_end(animate=False)


async def main(cx: SSHContext) -> None:
    cx.console.set_window_title("oneliners")
    await OnlinersApp(
        cx,
        art_path=path.join("userland", "artwork", "oneliners.ans"),
        art_encoding="amiga",
    ).run_async()
