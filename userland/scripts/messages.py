"""Oneliners script"""

# stdlib
from dataclasses import dataclass

# 3rd party
from textual import events
from textual.widgets import Label, ListItem, ListView, MarkdownViewer

# api
from xthulu.resources import Resources
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext

# local
from xthulu.models import Message

LIMIT = 200
"""The maximum number of messages to keep loaded in the UI at once"""


@dataclass
class MessageFilter:

    """Data class for filtering messages"""

    author: int | None = None
    """User ID of message author to filter for"""

    private = False
    """If `True`, show private messages; if `False`, show public messages"""

    tag: str | None = None
    """Tag name to filter for"""


class MessagesApp(BannerApp):

    """Message bases Textual app"""

    CSS = """
        $accent: ansi_yellow;
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

        ListView ListItem.--highlight {
            background: $accent 50%;
        }

        ListView:focus ListItem.--highlight {
            background: $accent;
        }
    """
    """Stylesheet"""

    filter: MessageFilter
    """Current message filter"""

    def __init__(
        self,
        context: SSHContext,
        **kwargs,
    ):
        self.filter = MessageFilter()
        super().__init__(context, **kwargs)

    def compose(self):
        for widget in super().compose():
            yield widget

        list = ListView()
        list.focus()
        yield list

        mv = MarkdownViewer(show_table_of_contents=False)
        mv.display = False
        yield mv

    async def key_escape(self, event: events.Key):
        lv = self.query_one(ListView)

        if lv.display:
            await self.action_quit()
            return

        mv = self.query_one(MarkdownViewer)
        mv.display = False
        lv.display = True
        lv.focus()
        event.stop()

    async def on_list_view_selected(self, event: ListView.Selected):
        self.query_one(ListView).display = False
        assert event.item.id
        message_id = int(event.item.id.split("_")[1])
        message: Message = await Message.get(message_id)
        mv = self.query_one(MarkdownViewer)
        mv.document.update(message.content)
        mv.display = True
        mv.scroll_home(animate=False)
        mv.focus()

    async def on_ready(self):
        await super().on_ready()
        db = Resources().db
        messages: list[dict] = await db.all(
            Message.select("id", "title")
            .order_by(Message.id.desc())
            .limit(LIMIT)
        )
        lv: ListView = self.query_one(ListView)

        for idx, m in enumerate(messages):
            lv.mount(
                ListItem(
                    Label(m["title"]),
                    id=f"message_{m['id']}",
                    classes="even" if idx % 2 else "",
                )
            )

        lv.index = 0
        lv.focus()


async def main(cx: SSHContext):
    cx.term.set_window_title("messages")
    await MessagesApp(
        cx, art_path="userland/artwork/messages.ans", art_encoding="amiga"
    ).run_async()
