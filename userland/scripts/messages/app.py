"""Messages Textual app"""

# stdlib
from asyncio import sleep
from datetime import datetime

# 3rd party
from textual import events
from textual.app import ComposeResult
from textual.css.query import NoMatches
from textual.widgets import Footer, Label, ListItem, ListView

# api
from xthulu.models import User
from xthulu.resources import Resources
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext

# local
from userland.models import Message
from userland.models.message.api import (
    get_latest_messages,
    get_newer_messages,
    get_older_messages,
)
from .editor_screen import EditorScreen
from .filter_modal import FilterModal
from .view_screen import ViewScreen

db = Resources().db

RATE_LIMIT_SECONDS = 3
"""Time to wait before allowing refresh after empty query result"""


class MessageFilter:
    """Data class for filtering messages"""

    private = False
    """If `True`, show private messages; if `False`, show public messages"""

    tags: list[str] | None = None
    """Tag name(s) to filter for"""


class MessagesApp(BannerApp):
    """Message bases Textual app"""

    BINDINGS = [
        ("f", "filter", "Filter"),
        ("n", "compose", "Compose"),
        ("r", "reply", "Reply"),
        ("escape", "", "Exit"),
    ]

    CSS = """
        $highlight: ansi_yellow;

        ListItem {
            background: $primary-background;
            layout: horizontal;
        }

        ListItem.even {
            background: $secondary-background;
        }

        ListView ListItem.--highlight {
            background: $highlight 50%;
        }

        ListView:focus ListItem.--highlight {
            background: $highlight;
        }

        ListItem Label.message_id {
            margin-right: 1;
        }
    """
    """Stylesheet"""

    filter: MessageFilter
    """Current message filter"""

    _first = -1
    """Newest message ID"""

    _last = -1
    """Oldest message ID"""

    _recent_query: datetime | None = None
    """Time of last query"""

    _last_query_empty = False
    """If last query had no results"""

    def __init__(
        self,
        context: SSHContext,
        **kwargs,
    ):
        self.filter = MessageFilter()
        super().__init__(context, **kwargs)

    async def _allow_refresh(self) -> bool:
        """Avoid database call for a while if last refresh was empty."""

        now = datetime.utcnow()
        if (
            self._recent_query is not None
            and self._last_query_empty
            and (now - self._recent_query).total_seconds() < RATE_LIMIT_SECONDS
        ):
            return False

        self._recent_query = now
        return True

    async def _load_messages(self, newer=False) -> None:
        """Load messages and append/prepend to ListView."""

        lv: ListView = self.query_one(ListView)
        first = len(lv.children) == 0
        limit = lv.region.height * 2
        query_limit = lv.region.height * (2 if first else 1)
        messages: dict

        if first:
            messages = await get_latest_messages(self.filter.tags, query_limit)
        elif newer:
            messages = await get_newer_messages(
                self._last, self.filter.tags, query_limit
            )
        else:
            messages = await get_older_messages(
                self._first, self.filter.tags, query_limit
            )

        # remember if result was empty for rate limiting refresh
        if not messages:
            self._last_query_empty = True
        else:
            self._last_query_empty = False

        coros = []

        # append/prepend items to ListView
        for idx, m in enumerate(messages):
            message_id = int(m["id"])

            if self._first == -1 or message_id < self._first:
                self._first = message_id

            if self._last == -1 or message_id > self._last:
                self._last = message_id

            item = ListItem(
                Label(
                    f"[italic][white]({m['id']})[/][/]", classes="message_id"
                ),
                Label(m["title"], classes="message_title", markup=False),
                id=f"message_{m['id']}",
                classes="even" if idx % 2 else "",
            )

            coros.append(lv.append(item))

            # add to top if pulling newer messages
            if newer and not first:
                lv.move_child(item, before=0)

        # if this is the first load, we're done!
        if first:
            for c in coros:
                await c

            return

        count = len(lv.children)
        last_index = lv.index or 0

        # trim ListView items to limit
        if count > limit:
            lv.index = None
            how_many = count - limit

            for _ in range(how_many):
                if newer:
                    # remove from bottom if loading newer items
                    coros.append(lv.children[-1].remove())
                else:
                    # remove from top if loading older items
                    coros.append(lv.children[0].remove())

            # fix CSS striping
            for idx, c in enumerate(lv.children):
                c.set_classes("even" if idx % 2 else "")

            # set new first/last message ID
            assert lv.children[-1].id
            self._first = int(lv.children[-1].id.split("_")[1])
            assert lv.children[0].id
            self._last = int(lv.children[0].id.split("_")[1])

            # restore ListView selection index
            if newer:
                lv.index = how_many
            else:
                lv.index = last_index - how_many

        for c in coros:
            await c

        # keep selected item in view
        lv.scroll_to_widget(lv.children[lv.index], animate=False)  # type: ignore

    async def _update_tags(self, tags: list[str]) -> None:
        lv = self.query_one(ListView)
        await lv.clear()
        self.filter.tags = [t for t in tags if t != ""]
        await self._load_messages()
        lv.index = 0
        lv.focus()

    def compose(self) -> ComposeResult:
        # load widgets from BannerApp
        for widget in super().compose():
            yield widget

        yield ListView(id="messages_list")
        yield Footer()

    async def action_compose(self) -> None:
        try:
            self.query_one(ListView)
        except NoMatches:
            # not in message list screen; pop screen first
            self.pop_screen()
            return await self.action_compose()

        await self.push_screen(EditorScreen())

    async def action_filter(self) -> None:
        try:
            self.query_one(ListView)
        except NoMatches:
            # not in message list screen; pop screen first
            self.pop_screen()
            return await self.action_filter()

        await self.push_screen(
            FilterModal(tags=self.filter.tags), self._update_tags
        )

    async def action_reply(self) -> None:
        try:
            lv: ListView = self.query_one(ListView)
        except NoMatches:
            # not in message list screen; pop screen first
            self.pop_screen()
            return await self.action_reply()

        assert lv.index is not None
        selected = lv.children[lv.index]
        assert selected.id
        message_id = int(selected.id.split("_")[1])
        message: Message = await db.one(
            Message.load(author=User.on(Message.author_id == User.id)).where(
                Message.id == message_id
            )
        )
        await self.push_screen(
            EditorScreen(
                content=(
                    f"\n\n---\n\n{message.author.name} wrote:"
                    f"\n\n{message.content}"
                ),
                reply_to=message,
            )
        )

    async def on_key(self, event: events.Key) -> None:
        if event.key not in [
            "down",
            "end",
            "escape",
            "home",
            "pagedown",
            "pageup",
            "up",
        ]:
            return

        try:
            lv: ListView = self.get_widget_by_id("messages_list")  # type: ignore
        except NoMatches:
            # we're not in the messages list screen; bail out
            return

        if event.key == "escape":
            self.exit()

        if event.key in ("home", "pageup"):
            if lv.index == 0 and self._allow_refresh():
                # hit top boundary; load newer messages
                await self._load_messages(newer=True)

            lv.index = 0

        elif event.key in ("end", "pagedown"):
            last = len(lv.children) - 1

            if lv.index == last and self._allow_refresh():
                # hit bottom boundary; load older messages
                await self._load_messages()

            lv.index = last

        elif event.key == "up" and lv.index == 0 and self._allow_refresh():
            # hit top boundary; load newer messages
            await self._load_messages(newer=True)

        elif (
            event.key == "down"
            and lv.index == len(lv.children) - 1
            and self._allow_refresh()
        ):
            # hit bottom boundary; load older messages
            await self._load_messages()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Load selected message in MarkdownViewer."""

        assert event.item.id
        message_id = int(event.item.id.split("_")[1])
        message: Message = await Message.get(message_id)
        await self.push_screen(ViewScreen(message=message))

    async def on_event(self, event: events.Event | events.MouseScrollDown):
        await super().on_event(event)
        scroll = False
        down = False

        if isinstance(event, events.MouseScrollDown):
            scroll = True
            down = True

        elif isinstance(event, events.MouseScrollUp):
            scroll = True
            down = False

        if not scroll:
            return

        try:
            lv = self.query_one(ListView)
        except NoMatches:
            # no ListView; might be in modal/editor
            return

        if down and lv.is_vertical_scroll_end and await self._allow_refresh():
            await self._load_messages()
            lv.index = len(lv.children) - round(lv.region.height * 1.25)
            lv.scroll_end(animate=False)
            lv.scroll_to(None, lv.index, animate=False)

        elif (
            not down and lv.scroll_offset.y == 0 and await self._allow_refresh()
        ):
            await self._load_messages(newer=True)
            lv.index = round(lv.region.height * 1.25)
            lv.scroll_home(animate=False)
            lv.scroll_to(None, lv.index - lv.region.height + 1, animate=False)

    async def on_ready(self) -> None:
        """App is ready; load messages."""

        # halt briefly for banner to fully load
        await sleep(0.1)
        await self._load_messages()
        lv = self.query_one(ListView)
        lv.index = 0
        lv.focus()
