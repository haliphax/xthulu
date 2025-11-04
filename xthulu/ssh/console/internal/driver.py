"""Console driver"""

# stdlib
from asyncio import QueueEmpty
from codecs import getincrementaldecoder
from time import sleep

# 3rd party
from textual import events
from textual._parser import ParseError
from textual._xterm_parser import XTermParser
from textual.drivers.linux_driver import LinuxDriver

# local
from ...context import SSHContext
from ..app import XthuluApp


class SSHDriver(LinuxDriver):
    """
    Textual console driver integrated with `xthulu.ssh.context.SSHContext`
    queues
    """

    context: SSHContext
    """The current SSH context"""

    def __init__(self, app: XthuluApp, **kwargs) -> None:
        self.context = app.context

        if "size" in kwargs:
            del kwargs["size"]

        super().__init__(
            app,
            size=self._get_terminal_size(),
            **kwargs,
        )

    def _get_terminal_size(self) -> tuple[int, int]:
        return (self.context.console.width, self.context.console.height)

    def flush(self) -> None:
        pass

    def run_input_thread(self) -> None:
        """Wait for input and dispatch events."""

        parser = XTermParser(self._debug)
        feed = parser.feed
        tick = parser.tick
        utf8_decoder = getincrementaldecoder("utf-8")().decode
        decode = utf8_decoder

        while not self.exit_event.is_set():
            try:
                unicode_data = decode(self.context.input.get_nowait())

                for event in feed(unicode_data):
                    if isinstance(event, events.CursorPosition):
                        self.cursor_origin = (event.x, event.y)
                    else:
                        self.process_message(event)
            except QueueEmpty:
                sleep(0.01)
            except ParseError:
                break

            for event in tick():
                if isinstance(event, events.CursorPosition):
                    self.cursor_origin = (event.x, event.y)
                else:
                    self.process_message(event)

        try:
            for event in feed(""):
                pass
        except ParseError:
            pass

    def write(self, data: str) -> None:
        try:
            self.context.proc.stdout.write(data.encode(self.context.encoding))
        except BrokenPipeError:
            # process is likely closing
            pass
