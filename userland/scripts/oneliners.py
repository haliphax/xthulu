"""Oneliners script"""

# stdlib
from os import path

# 3rd party
from sqlmodel import col, select
from textual.widgets import Input, Label, ListItem, ListView

# api
from xthulu.resources import db_session
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext

# local
from userland.models import Oneliner

LIMIT = 200
"""Total number of oneliners to load"""


class OnelinersApp(BannerApp):
    """Oneliners Textual app"""

    CSS = """
        $accent: ansi_red;

        Label {
            width: 100%;
        }

        ListView {
            width: 100%;
        }

        ListItem {
            background: $primary-background;
        }

        ListItem.even {
            background: $secondary-background;
        }

        ListView:focus ListItem.-highlight {
            background: $accent;
        }
    """
    """Stylesheet"""

    def __init__(self, context: SSHContext, **kwargs):
        super(OnelinersApp, self).__init__(context, **kwargs)
        self.bind("escape", "quit")

    def compose(self):
        for widget in super(OnelinersApp, self).compose():
            yield widget

        # oneliners
        lv = ListView()
        lv.styles.scrollbar_background = "black"
        lv.styles.scrollbar_color = "ansi_yellow"
        lv.styles.scrollbar_color_active = "white"
        lv.styles.scrollbar_color_hover = "ansi_bright_yellow"
        yield lv

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
            async with db_session() as db:
                db.add(Oneliner(message=val, user_id=self.context.user.id))
                await db.commit()

        self.exit()

    async def on_mount(self) -> None:
        recent = (
            select(Oneliner.id)
            .order_by(col(Oneliner.id).desc())
            .limit(LIMIT)
            .alias("recent")
            .select()
        )

        async with db_session() as db:
            oneliners = (
                await db.exec(
                    select(Oneliner).where(col(Oneliner.id).in_(recent))
                )
            ).all()

        lv = self.query_one(ListView)

        for idx, o in enumerate(oneliners):
            lv.mount(
                ListItem(Label(o.message), classes="even" if idx % 2 else "")
            )

        lv.index = len(oneliners) - 1
        lv.scroll_end(animate=False)


async def main(cx: SSHContext) -> None:
    cx.console.set_window_title("oneliners")
    await OnelinersApp(
        cx,
        art_path=path.join("userland", "artwork", "oneliners.ans"),
        art_encoding="amiga",
        alt="79 Columns // Oneliners",
    ).run_async()
