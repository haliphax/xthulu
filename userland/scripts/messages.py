"""Messages script"""

# stdlib
from datetime import datetime

# 3rd party
from textual import events
from textual.widgets import Label, ListItem, ListView, MarkdownViewer

# api
from xthulu.models import Message
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext

LIMIT = 50
"""The maximum number of messages to keep loaded in the UI at once"""

LOAD_AT_ONCE = round(LIMIT / 2)
"""How many messages to load at a time dynamically when navigating ListView"""


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

    _first = -1
    _last = -1
    _recent_query: datetime | None = None
    _last_query_empty = False

    def __init__(
        self,
        context: SSHContext,
        **kwargs,
    ):
        self.filter = MessageFilter()
        super().__init__(context, **kwargs)

    async def _allow_refresh(self):
        now = datetime.utcnow()

        # avoid database call for a while if last refresh was empty
        if (
            self._recent_query is not None
            and self._last_query_empty
            and (now - self._recent_query).total_seconds() < 10
        ):
            return False

        self._recent_query = now
        return True

    async def _load_messages(self, newer=False):
        lv: ListView = self.query_one(ListView)
        select = Message.select("id", "title")
        first = len(lv.children) == 0
        limit = min(round(lv.size.height / 2), LOAD_AT_ONCE)

        if first:
            limit = min(lv.size.height, LIMIT)
            query = select.order_by(Message.id.desc())
        elif newer:
            query = select.where(Message.id > self._last).order_by(Message.id)
        else:
            query = select.where(Message.id < self._first).order_by(
                Message.id.desc()
            )

        messages: list[dict] = await query.limit(limit).gino.all()

        if not messages:
            self._last_query_empty = True
        else:
            self._last_query_empty = False

        for idx, m in enumerate(messages):
            message_id = int(m["id"])

            if self._first == -1 or message_id < self._first:
                self._first = message_id

            if self._last == -1 or message_id > self._last:
                self._last = message_id

            item = ListItem(
                Label(m["title"], markup=False),
                id=f"message_{m['id']}",
                classes="even" if idx % 2 else "",
            )

            lv.append(item)

            if newer and not first:
                lv.move_child(item, before=0)

        if first:
            return

        count = len(lv.children)
        last_index = lv.index or 0

        if count > lv.size.height:
            lv.index = None
            how_many = count - lv.size.height

            for _ in range(how_many):
                if newer:
                    lv.children[-1].remove()
                else:
                    lv.children[0].remove()

            for idx, c in enumerate(lv.children):
                c.set_classes("even" if idx % 2 else "")

            assert lv.children[-1].id
            self._first = int(lv.children[-1].id.split("_")[1])
            assert lv.children[0].id
            self._last = int(lv.children[0].id.split("_")[1])

            if newer:
                lv.index = how_many
            else:
                lv.index = last_index - how_many

            lv.scroll_to_widget(lv.children[lv.index])

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

    async def on_key(self, event: events.Key):
        lv = self.query_one(ListView)

        if not lv.display:
            return

        if event.key not in ["down", "up", "home", "end"]:
            return

        if event.key == "home":
            lv.index = 0
        elif event.key == "end":
            lv.index = len(lv.children) - 1
        if event.key == "up" and lv.index == 0 and self._allow_refresh():
            await self._load_messages(newer=True)
        elif (
            event.key == "down"
            and lv.index == len(lv.children) - 1
            and self._allow_refresh()
        ):
            await self._load_messages()

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
        await self._load_messages()
        lv = self.query_one(ListView)
        lv.index = 0
        lv.focus()


async def main(cx: SSHContext):
    cx.console.set_window_title("messages")
    await MessagesApp(
        cx, art_path="userland/artwork/messages.ans", art_encoding="amiga"
    ).run_async()
