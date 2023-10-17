"""Console driver"""

# stdlib
from asyncio import QueueEmpty
from codecs import getincrementaldecoder
from time import sleep

# 3rd party
from textual._parser import ParseError
from textual._xterm_parser import XTermParser
from textual.drivers.linux_driver import LinuxDriver

# local
from ...context import SSHContext
from ..app import XthuluApp


class SSHDriver(LinuxDriver):

    """Textual console driver integrated with SSHContext queues"""

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
        parser = XTermParser(lambda: True, self._debug)
        feed = parser.feed
        decode = getincrementaldecoder("utf-8")().decode

        while not self.exit_event.is_set():
            try:
                r = self.context.input.get_nowait()
                unicode_data = decode(r)

                for event in feed(unicode_data):
                    self.process_event(event)

            except QueueEmpty:
                sleep(0.01)
                pass

            except ParseError:
                # process is likely closing; end the loop
                break

    def write(self, data: str) -> None:
        try:
            self.context.proc.stdout.write(data.encode(self.context.encoding))
        except BrokenPipeError:
            # process is likely closing
            pass
