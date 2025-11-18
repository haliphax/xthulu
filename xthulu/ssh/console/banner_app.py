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


class BannerApp(XthuluApp[ReturnType]):
    """Textual app with banner display"""

    BANNER_PADDING = 10
    """Required space left over to display banner art"""

    _alt: str
    """Alternate text if banner won't fit"""

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
        "" # empty docstring
        self.art_encoding = art_encoding
        self.art_path = art_path
        self.artwork = []
        self._alt = f"{alt}\n"
        super(BannerApp, self).__init__(context=context, **kwargs)

    def compose(self) -> ComposeResult:
        "" # empty docstring
        self.banner = Static(id="banner", markup=False)
        yield self.banner

    def _check_size(self, width: int, height: int) -> None:
        # assumes art is 80 columns wide; improve this
        lines = len(self.artwork)
        pad_left = floor(self.context.console.width / 2 - 40)
        self.banner.styles.margin = (0, pad_left)
        self.banner.styles.width = 80
        self.banner.styles.height = lines

        if width < lines + self.BANNER_PADDING or self.console.width < 80:
            self.banner.styles.height = len(self._alt.splitlines())
            self.banner.update(self._alt)
        elif lines > 0:
            self.banner.styles.height = lines
            text = Text.from_ansi(
                "".join(self.artwork), overflow="ignore", end=""
            )
            self.banner.update(text)

    async def on_mount(self) -> None:
        self.artwork = await load_art(self.art_path, self.art_encoding)
        self._check_size(self.console.width, self.console.height)

    def on_resize(self, event: events.Resize) -> None:
        self._check_size(event.size.width, event.size.height)
