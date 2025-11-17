"""Messages Textual app"""

# stdlib
from asyncio import sleep
from datetime import datetime
from typing import Sequence, Tuple

# 3rd party
from sqlalchemy.orm import joinedload
from sqlmodel import select
from textual import events
from textual.app import ComposeResult, ScreenStackError
from textual.widgets import Footer, Label, ListItem, ListView

# api
from xthulu.resources import db_session
from xthulu.ssh.console.banner_app import BannerApp
from xthulu.ssh.context import SSHContext

# local
from userland.models import Message, MessageTags
from userland.models.message.api import (
    get_latest_messages,
    get_newer_messages,
    get_older_messages,
)
from .editor_screen import EditorScreen
from .filter_modal import FilterModal
from .view_screen import ViewScreen

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
        ("escape", "quit", "Exit"),
        ("n", "compose", "Compose"),
        ("r", "reply", "Reply"),
        ("f", "filter", "Filter"),
    ]

    CSS = """
        $highlight: ansi_magenta;

        Footer, Footer:ansi {
            &,
            .footer-key--key,
            .footer-key--description {
                background: #007 100%;
                color: #077;
            }

            .footer-key--key {
                color: #0ff;
            }

            FooterKey:hover,
            FooterKey:hover .footer-key--key {
                background: #077 100%;
                color: #fff;
            }
        }

        ListItem {
            background: $primary-background;
            layout: horizontal;
        }

        ListItem.even {
            background: $secondary-background;
        }

        ListView ListItem.-highlight {
            background: $highlight 100%;
        }

        ListView:focus ListItem.-highlight {
            background: $highlight 100%;
        }

        ListItem Label.message_id, ListItem Label.message_title {
            margin-right: 1;
        }

        ListItem Label.message_id {
            width: 8;
        }

        ListItem Label.message_title {
            width: 75%;
        }

        ListItem Label.message_author {
            align: right middle;
        }
    """

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
        super(MessagesApp, self).__init__(context, **kwargs)

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
        query_limit = limit if first else lv.region.height
        messages: Sequence[Tuple[int, str, str]]

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
        for idx, [message_id, title, author] in enumerate(messages):
            if self._first == -1 or message_id < self._first:
                self._first = message_id

            if self._last == -1 or message_id > self._last:
                self._last = message_id

            item = ListItem(
                Label(
                    f"[italic][white]#{message_id}[/][/]",
                    classes="message_id",
                ),
                Label(title, classes="message_title", markup=False),
                Label(author, classes="message_author", markup=False),
                id=f"message_{message_id}",
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

            # adjust CSS striping
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
        self.filter.tags = tags
        await self._load_messages()
        lv.index = 0
        lv.focus()

    def compose(self) -> ComposeResult:
        # load widgets from BannerApp
        for widget in super(MessagesApp, self).compose():
            yield widget

        yield ListView(id="messages_list")
        yield Footer()

    async def action_compose(self) -> None:
        if self.screen.id != "_default":
            # not in message list screen; pop screen first
            self.pop_screen()
            return await self.action_compose()

        await self.push_screen(EditorScreen())

    async def action_filter(self) -> None:
        if self.screen.id != "_default":
            return

        await self.push_screen(
            FilterModal(tags=self.filter.tags),
            self._update_tags,  # type: ignore
        )

    async def action_reply(self) -> None:
        # not in message list screen; pop screen first
        if self.screen.id != "_default":
            self.pop_screen()
            return await self.action_reply()

        lv: ListView = self.query_one(ListView)
        assert lv.index is not None
        selected = lv.children[lv.index]
        assert selected.id
        message_id = int(selected.id.split("_")[1])

        async with db_session() as db:
            message: Message = (
                await db.exec(
                    select(Message)
                    .where(Message.id == message_id)
                    .options(joinedload(Message.author))  # type: ignore
                )
            ).one()

            await self.push_screen(
                EditorScreen(
                    content=(
                        "\n\n---"
                        f"\n\n{
                            message.author.name if message.author else 'Unknown'
                        } wrote:"
                        f"\n\n{message.content}"
                    ),
                    reply_to=message,
                )
            )

    async def action_quit(self) -> None:
        self.exit()

    async def on_key(self, event: events.Key) -> None:
        if self.screen.id != "_default":
            return

        if event.key not in [
            "down",
            "end",
            "home",
            "pagedown",
            "pageup",
            "up",
        ]:
            return

        lv: ListView = self.get_widget_by_id("messages_list")  # type: ignore

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

        async with db_session() as db:
            message = (
                await db.exec(
                    select(Message)
                    .where(Message.id == message_id)
                    .options(
                        joinedload(Message.author),  # type: ignore
                        joinedload(Message.recipient),  # type: ignore
                    )
                )
            ).one()
            tags = (
                await db.exec(
                    select(MessageTags.tag_name).where(
                        MessageTags.message_id == message_id
                    )
                )
            ).all()

        assert message
        await self.push_screen(ViewScreen(message=message, tags=tags))

    async def on_event(self, event: events.Event | events.MouseScrollDown):
        await super(MessagesApp, self).on_event(event)

        try:
            if self.screen.id != "_default":
                return
        except ScreenStackError:
            return

        down = False

        if isinstance(event, events.MouseScrollDown):
            down = True
        elif isinstance(event, events.MouseScrollUp):
            down = False
        else:
            return

        lv = self.query_one(ListView)

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
