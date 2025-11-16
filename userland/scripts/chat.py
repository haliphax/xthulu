"""Node chat script"""

# stdlib
from asyncio import Event
from collections import deque
import json

# 3rd party
from pydantic import BaseModel
from redis import Redis
from redis.client import PubSub
from rich.markup import escape
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Input, Static

# api
from xthulu.resources import Resources
from xthulu.ssh.console.app import XthuluApp
from xthulu.ssh.context import SSHContext

LIMIT = 1000
"""Total number of messages to keep in backlog"""

MAX_LENGTH = 256
"""Maximum length of individual messages"""


class ChatMessage(BaseModel):
    user: str | None
    message: str


class ChatApp(XthuluApp):
    """Node chat Textual app"""

    BINDINGS = [Binding("escape", "quit", show=False)]

    redis: Redis
    """Redis connection"""

    pubsub: PubSub
    """Redis PubSub connection"""

    _chatlog: deque[ChatMessage]
    _exit_event: Event

    def __init__(self, context: SSHContext, **kwargs):
        super(ChatApp, self).__init__(context, **kwargs)
        self.redis = Resources().cache
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(**{"chat": self.on_chat})
        self._chatlog = deque(maxlen=LIMIT)
        self._exit_event = Event()
        self.run_worker(self._listen, exclusive=True, thread=True)

    def _listen(self) -> None:
        self.redis.publish(
            "chat",
            ChatMessage(
                user=None, message=f"{self.context.username} has joined"
            ).model_dump_json(),
        )

        while not self._exit_event.is_set():
            self.pubsub.get_message(True, 0.01)

    def compose(self):
        # chat log
        yield VerticalScroll(Static(id="log"))

        # input
        input_widget = Input(
            placeholder="Enter a message or press ESC",
            max_length=MAX_LENGTH,
        )
        input_widget.focus()
        yield input_widget

    def on_chat(self, message: dict[str, str]) -> None:
        def format_message(msg: ChatMessage):
            if msg.user:
                return (
                    f"\n[bright_white on blue]<{msg.user}>[/] "
                    f"{escape(msg.message)}"
                )

            return (
                "\n[bright_white on red]<*>[/] "
                f"[italic][white]{msg.message}[/][/]"
            )

        msg = ChatMessage(**json.loads(message["data"]))
        self._chatlog.append(msg)
        l: Static = self.get_widget_by_id("log")  # type: ignore
        l.update(
            self.console.render_str(
                "".join([format_message(m) for m in self._chatlog])
            )
        )
        vs = self.query_one(VerticalScroll)
        vs.scroll_end(animate=False)
        input = self.query_one(Input)
        input.value = ""

    def exit(self, **kwargs) -> None:
        msg = ChatMessage(
            user=None, message=f"{self.context.username} has left"
        )
        self.redis.publish("chat", msg.model_dump_json())
        self._exit_event.set()
        self.workers.cancel_all()
        super(ChatApp, self).exit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        val = event.input.value.strip()

        if val == "":
            return

        self.redis.publish(
            "chat",
            ChatMessage(
                user=self.context.username, message=val
            ).model_dump_json(),
        )


async def main(cx: SSHContext) -> None:
    cx.console.set_window_title("chat")
    await ChatApp(cx).run_async()
