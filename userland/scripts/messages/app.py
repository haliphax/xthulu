"""Messages Textual app"""

# stdlib
from datetime import datetime

# 3rd party
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.widgets import Footer, Label, ListItem, ListView

# api
from xthulu.models import User
from xthulu.resources import Resources
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext

# local
from userland.models import Message, MessageTags
from .editor_screen import EditorScreen
from .filter_modal import FilterModal
from .view_screen import ViewScreen

db = Resources().db

LIMIT = 50
"""The maximum number of messages to keep loaded in the UI at once"""

LOAD_AT_ONCE = round(LIMIT / 2)
"""Maximum messages to load at a time dynamically when navigating ListView"""

RATE_LIMIT_SECONDS = 10
"""Time to wait before allowing refresh after empty query result"""


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

    BINDINGS = [
        Binding("f", "filter", "Filter"),
        Binding("n", "compose", "Compose"),
        Binding("r", "reply", "Reply"),
        Binding("escape", "", "Exit"),
    ]

    CSS = """
        $highlight: ansi_yellow;
        $error: ansi_bright_red;

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

    _tags = []
    """List of tags to filter by"""

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
        select = Message.select("id", "title")
        filter = (
            select
            if len(self._tags) == 0
            else select.select_from(
                Message.join(
                    MessageTags,
                    db.and_(
                        MessageTags.message_id == Message.id,
                        MessageTags.tag_name.in_(self._tags),
                    ),
                )
            )
        )
        first = len(lv.children) == 0
        limit = min(round(lv.size.height / 2), LOAD_AT_ONCE)

        if first:
            # app startup; load most recent messages
            limit = min(lv.size.height, LIMIT)
            query = filter.order_by(Message.id.desc())
        elif newer:
            # load newer messages
            query = filter.where(Message.id > self._last).order_by(Message.id)
        else:
            # load older messages
            query = filter.where(Message.id < self._first).order_by(
                Message.id.desc()
            )

        messages: list[dict] = await query.limit(limit).gino.all()

        # remember if result was empty for rate limiting refresh
        if not messages:
            self._last_query_empty = True
        else:
            self._last_query_empty = False

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

            lv.append(item)

            # add to top if pulling newer messages
            if newer and not first:
                lv.move_child(item, before=0)

        # if this is the first load, we're done!
        if first:
            return

        count = len(lv.children)
        last_index = lv.index or 0

        # trim ListView items to limit
        if count > lv.size.height:
            lv.index = None
            how_many = count - lv.size.height

            for _ in range(how_many):
                if newer:
                    # remove from bottom if loading newer items
                    lv.children[-1].remove()
                else:
                    # remove from top if loading older items
                    lv.children[0].remove()

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

            # keep selected item in view
            lv.scroll_to_widget(lv.children[lv.index])

    async def _update_tags(self, tags: list[str]) -> None:
        lv = self.query_one(ListView)
        await lv.clear()
        self._tags = [t for t in tags if t != ""]
        await self._load_messages()
        lv.index = 0
        lv.focus()

    def compose(self) -> ComposeResult:
        # load widgets from BannerApp
        for widget in super().compose():
            yield widget

        # messages list
        list = ListView(id="messages_list")
        list.focus()
        yield list

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

        await self.push_screen(FilterModal(tags=self._tags), self._update_tags)

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

    async def on_ready(self) -> None:
        """App is ready; load messages."""

        await self._load_messages()
        lv = self.query_one(ListView)
        lv.index = 0
        lv.focus()
