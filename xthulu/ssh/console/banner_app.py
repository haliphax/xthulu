"""Textual application wrapper with display banner"""

# stdlib
from math import floor

# 3rd party
from rich.text import Text
from textual import events
from textual.app import ComposeResult, ReturnType
from textual.widgets import Static

# local
from ..context import SSHContext
from .app import XthuluApp
from .art import load_art

BANNER_PADDING = 10
"""Required space left over to display banner art"""


class BannerApp(XthuluApp[ReturnType]):
    """Textual app with banner display"""

    _alt: str

    art_encoding: str
    """Encoding of the artwork file"""

    art_path: str
    """Path to the artwork file"""

    artwork: list[str]
    """Lines from loaded banner artwork"""

    banner: Static
    """Banner widget"""

    def __init__(
        self,
        context: SSHContext,
        art_path: str,
        art_encoding: str,
        alt: str,
        **kwargs,
    ):
        self.art_encoding = art_encoding
        self.art_path = art_path
        self.artwork = []
        self._alt = f"{alt}\n"
        super(BannerApp, self).__init__(context=context, **kwargs)

    def _update_banner(self):
        padded = []
        # assumes art is 80 columns wide; improve this
        pad_left = " " * floor(self.context.console.width / 2 - 40)

        for line in self.artwork:
            padded += [pad_left, line]

        text = Text.from_ansi(
            "".join(padded), overflow="crop", no_wrap=True, end=""
        )
        self.banner.update(text)

    def compose(self) -> ComposeResult:
        # banner
        self.banner = Static(id="banner", markup=False)
        lines = len(self.artwork)

        if (
            self.console.height < lines + BANNER_PADDING
            or self.console.width < 80
        ):
            self.banner.update(self._alt)
        elif lines > 0:
            self._update_banner()

        yield self.banner

    async def on_mount(self):
        self.artwork = await load_art(self.art_path, self.art_encoding)
        self._update_banner()

    def on_resize(self, event: events.Resize) -> None:
        if (
            event.size.height < len(self.artwork) + BANNER_PADDING
            or event.size.width < 80
        ):
            self.banner.update(self._alt)
        else:
            self._update_banner()
