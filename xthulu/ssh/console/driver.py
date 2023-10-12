"""Console driver"""

# 3rd party
from asyncio import run_coroutine_threadsafe
from codecs import getincrementaldecoder
from textual._parser import ParseError
from textual._xterm_parser import XTermParser
from textual.drivers.linux_driver import LinuxDriver

# local
from ..context import SSHContext
from .app import XthuluApp


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
        return (self.context.term.width, self.context.term.height)

    def flush(self) -> None:
        pass

    def run_input_thread(self) -> None:
        parser = XTermParser(self.context.proc.stdin.at_eof, self._debug)
        feed = parser.feed
        decode = getincrementaldecoder("utf-8")().decode

        while not self.exit_event.is_set():
            try:
                r = run_coroutine_threadsafe(
                    self.context.input.get(), self._loop
                ).result()
                unicode_data = decode(r)

                for event in feed(unicode_data):
                    self.process_event(event)

            except ParseError:
                # process is likely closing; end the loop
                return

        # avoid input debuffering bug on close
        self.context.proc.stdin.feed_data(b"\r\n")

    def write(self, data: str) -> None:
        try:
            self.context.proc.stdout.write(data.encode(self.context.encoding))
        except BrokenPipeError:
            # process is likely closing
            pass
