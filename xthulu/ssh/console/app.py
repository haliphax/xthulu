"""Textual application wrapper"""

# stdlib
from asyncio import sleep

# 3rd party
from rich.segment import Segments
from textual import events
from textual.app import App, ReturnType
from textual.geometry import Size

# local
from ...logger import log
from ..context import SSHContext


class _ErrorConsoleProxy:
    def print(self, what, **kwargs):
        if isinstance(what, Segments):
            log.error("".join([s.text for s in what.segments]))
            return

        log.error(what)


class XthuluApp(App[ReturnType]):
    """SSH wrapper for Textual apps"""

    ENABLE_COMMAND_PALETTE = False
    """Command palette is disabled by default"""

    context: SSHContext
    """The current SSH context"""

    def __init__(self, context: SSHContext, ansi_color=True, **kwargs):
        ""  # empty docstring
        # avoid cyclic import
        from .internal.driver import SSHDriver

        super(XthuluApp, self).__init__(
            driver_class=SSHDriver, ansi_color=ansi_color, **kwargs
        )
        self.context = context
        self.console = context.console
        self.error_console = _ErrorConsoleProxy()  # type: ignore
        self.run_worker(self._watch_for_resize, exclusive=True)

    async def _watch_for_resize(self):
        # avoid cyclic import
        from .internal.driver import SSHDriver

        while True:
            ev = self.context.events.get("resize")

            if not ev:
                await sleep(0.5)
                continue

            new_size = Size(*ev[-1].data)
            d: SSHDriver = self._driver  # type: ignore
            d.process_message(events.Resize(new_size, new_size))

    def exit(self, **kwargs) -> None:  # type: ignore
        ""  # empty docstring
        # avoid cyclic import
        from .internal.driver import SSHDriver

        super(XthuluApp, self).exit(**kwargs)
        d: SSHDriver = self._driver  # type: ignore
        d._disable_bracketed_paste()
        d._disable_mouse_support()
        d.exit_event.set()
