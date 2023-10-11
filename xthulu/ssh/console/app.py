# stdlib
from asyncio import sleep

# 3rd party
from textual import events
from textual.app import App
from textual.geometry import Size

from ...events.structs import EventData

# local
from ..context import SSHContext


class XthuluApp(App):

    """SSH wrapper for Textual apps"""

    context: SSHContext
    """The current SSH context"""

    def __init__(self, context: SSHContext, **kwargs):
        # avoid cyclic import
        from .driver import SSHDriver

        self.context = context
        super().__init__(driver_class=SSHDriver, **kwargs)
        self.console = context.term
        self.error_console = None
        self.run_worker(self._watch_for_resize, exclusive=True)

    async def _watch_for_resize(self):
        while True:
            ev: list[EventData] = self.context.events.get(
                "resize"
            )  # type: ignore

            if not ev:
                await sleep(0.5)
                continue

            new_size = Size(*ev[-1].data)
            self._driver.process_event(events.Resize(new_size, new_size))

    def exit(self, **kwargs) -> None:
        # avoid cyclic import
        from .driver import SSHDriver

        super().exit(**kwargs)
        self._driver: SSHDriver
        self._driver._disable_bracketed_paste()
        self._driver._disable_mouse_support()
        self._driver.exit_event.set()
