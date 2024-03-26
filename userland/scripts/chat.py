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
from textual.validation import Length
from textual.widgets import Input, Label, Static

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
    CSS = """
        $error: ansi_bright_red;

        #err {
            background: $error;
            color: black;
        }
    """
    """Stylesheet"""

    redis: Redis
    """Redis connection"""

    pubsub: PubSub
    """Redis PubSub connection"""

    _log: deque[ChatMessage]
    _exit_event: Event

    def __init__(self, context: SSHContext, **kwargs):
        super().__init__(context, **kwargs)
        self.redis = Resources().cache
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(**{"chat": self.on_chat})
        self._log = deque(maxlen=LIMIT)
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

        # error message
        err = Label(id="err")
        err.display = False
        yield err

        # input
        input_widget = Input(
            placeholder="Enter a message or press ESC",
            validators=Length(
                maximum=MAX_LENGTH,
                failure_description=(
                    f"Too long; must be <= {MAX_LENGTH} characters"
                ),
            ),
            validate_on=(
                "changed",
                "submitted",
            ),
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
        self._log.append(msg)
        l: Static = self.get_widget_by_id("log")  # type: ignore
        l.update(
            self.console.render_str(
                "".join([format_message(m) for m in self._log])
            )
        )
        vs = self.query_one(VerticalScroll)
        vs.scroll_end(animate=False)
        input = self.query_one(Input)
        input.value = ""

    def exit(self) -> None:
        msg = ChatMessage(
            user=None, message=f"{self.context.username} has left"
        )
        self.redis.publish("chat", msg.model_dump_json())
        self._exit_event.set()
        self.workers.cancel_all()
        super().exit()

    def on_input_changed(self, event: Input.Changed) -> None:
        err: Label = self.get_widget_by_id("err")  # type: ignore

        if not event.validation_result or event.validation_result.is_valid:
            err.display = False
            return

        message = "".join(
            (
                " ",
                "... ".join(event.validation_result.failure_descriptions),
            )
        )
        err.update(message)
        err.display = True

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.validation_result and not event.validation_result.is_valid:
            return

        val = event.input.value.strip()

        if val != "":
            self.redis.publish(
                "chat",
                ChatMessage(
                    user=self.context.username, message=val
                ).model_dump_json(),
            )


async def main(cx: SSHContext) -> None:
    cx.console.set_window_title("chat")
    await ChatApp(cx).run_async()
