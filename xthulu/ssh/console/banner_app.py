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
from .art import load_art

BANNER_PADDING = 10
"""Required space left over to display banner art"""


class BannerApp(XthuluApp):

    """Textual app with banner display"""

    art_encoding: str
    """Encoding of the artwork file"""

    art_path: str
    """Path to the artwork file"""

    artwork: list[str]
    """Lines from loaded banner artwork"""

    def __init__(
        self, context: SSHContext, art_path: str, art_encoding: str, **kwargs
    ):
        self.art_encoding = art_encoding
        self.art_path = art_path
        self.artwork = []
        super().__init__(context=context, **kwargs)

    def _update_banner(self):
        padded = []
        pad_left = " " * floor(self.context.term.width / 2 - 40)

        for line in self.artwork:
            padded += [pad_left, line]

        text = Text.from_ansi(
            "".join(padded), overflow="crop", no_wrap=True, end=""
        )
        banner: Label = self.get_widget_by_id("banner")  # type: ignore
        banner.update(text)

    def compose(self):
        # banner
        banner = Label(id="banner", markup=False)
        lines = len(self.artwork)

        if self.console.height < lines + BANNER_PADDING:
            banner.display = False
        elif lines > 0:
            self._update_banner()

        yield banner

    async def on_ready(self):
        self.artwork = await load_art(self.art_path, self.art_encoding)
        self._update_banner()

    def on_resize(self, event: events.Resize) -> None:
        # banner
        banner: Label = self.get_widget_by_id("banner")  # type: ignore

        if event.size.height < len(self.artwork) + BANNER_PADDING:
            banner.update("")
            banner.display = False
        else:
            self._update_banner()
            banner.display = True
