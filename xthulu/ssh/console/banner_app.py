"""Textual application wrapper with display banner"""

# stdlib
from math import floor

# 3rd party
from rich.text import Text
from textual import events
from textual.widgets import Label

# local
from ..context import SSHContext
from .app import XthuluApp

BANNER_PADDING = 10
"""Required space left over to display banner art"""


class BannerApp(XthuluApp):

    """Textual app with banner display"""

    artwork: list[str]
    """Lines from pre-loaded artwork file"""

    banner: Label
    """Artwork banner widget"""

    def __init__(self, context: SSHContext, artwork: list[str], **kwargs):
        self.artwork = artwork
        super().__init__(context=context, **kwargs)
        self.run_worker(self._watch_for_resize, exclusive=True)

    def _update_banner(self):
        padded = []
        pad_left = " " * floor(self.context.term.width / 2 - 40)

        for line in self.artwork:
            padded += [pad_left, line]

        text = Text.from_ansi(
            "".join(padded), overflow="crop", no_wrap=True, end=""
        )
        self.banner.update(text)

    def compose(self):
        # banner
        self.banner = Label(markup=False)

        if self.console.height < len(self.artwork) + BANNER_PADDING:
            self.banner.display = False
        else:
            self._update_banner()

        yield self.banner

    def on_resize(self, event: events.Resize) -> None:
        if event.size.height < len(self.artwork) + BANNER_PADDING:
            self.banner.update("")
            self.banner.display = False
        else:
            self._update_banner()
            self.banner.display = True
