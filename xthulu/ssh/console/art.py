"""Artwork display"""

# stdlib
from re import Match, sub

# 3rd party
import aiofiles as aiof
from rich.text import Text
from textual import events
from textual.widgets import Log

# local
from ..context import SSHContext
from .app import XthuluApp

FIND_CUF_REGEX = r"\x1b\[(\d+)C"


class ArtLog(XthuluApp):
    """Displays artwork"""

    artwork: list[str]
    delay: float

    def __init__(
        self,
        context: SSHContext,
        artwork: list[str],
        delay: float = 0.1,
        **kwargs,
    ):
        self.artwork = artwork
        self.delay = delay
        super().__init__(context, **kwargs)
        self.run_worker(self._worker, exclusive=True)

    @property
    def scrollbars_enabled(self) -> bool:
        return False

    def compose(self):
        yield Log()

    async def _worker(self):
        artlog: Log = self.query_one(Log)

        for line in self.artwork:
            if self._exit:
                return

            artlog.write_line(line)

            if self.context.inkey(timeout=0.1):
                break

        self.exit()

    async def on_key(self, _: events.Key):
        self.exit()


def _replace_cuf(match: Match[str]) -> str:
    return " " * int(match.group(1))


def normalize_ansi(text: str) -> str:
    """
    Replace CUF sequences with spaces.

    Args:
        text: The text to modify.

    Returns:
        Text with CUF sequences replaced by whitespace.
    """

    return sub(FIND_CUF_REGEX, _replace_cuf, text)


async def load_art(path: str, encoding="cp437") -> list[str]:
    """
    Load normalized, properly-encoded artwork files.

    Args:
        path: The path of the file to load.
        encoding: The encoding of the file to load.

    Returns:
        A list of normalized lines from the target file.
    """

    async with aiof.open(path, encoding=encoding) as f:
        artwork = [normalize_ansi(line) for line in await f.readlines()]

    return artwork


async def scroll_art_app(
    context: SSHContext, path: str, encoding="cp437", delay=0.1
):
    """
    Display ANSI artwork in a scrolling Log panel.

    Args:
        context: The current SSHContext.
        path: The path of the file to display.
        encoding: The encoding of the file to display.
        delay: The delay (in seconds) between displaying each line.
    """

    if context.encoding != "utf-8":
        encoding = context.encoding

    artwork = await load_art(path, encoding)
    await ArtLog(context, artwork, delay).run_async()


async def scroll_art(
    context: SSHContext, path: str, encoding="cp437", delay=0.1
) -> bytes | None:
    """
    Display ANSI artwork directly to the console.

    Args:
        context: The current SSHContext.
        path: The path of the file to display.
        encoding: The encoding of the file to display.
        delay: The delay (in seconds) between displaying each line.

    Returns:
        The byte sequence of a key pressed during display, if any.
    """

    if context.encoding != "utf-8":
        encoding = context.encoding

    artwork = await load_art(path, encoding)

    # show entire piece immediately if shorter than terminal
    if context.console.height >= len(artwork):
        delay = 0.0

    for line in artwork:
        processed = Text.from_ansi(line, overflow="crop", no_wrap=True, end="")
        context.console.print(
            processed,
            emoji=False,
            end="\n",
            height=1,
            highlight=False,
            markup=False,
            overflow="crop",
            no_wrap=True,
        )

        if delay <= 0:
            continue

        key = await context.inkey(timeout=delay)

        if key:
            return key


async def show_art(context: SSHContext, path: str, encoding="cp437") -> None:
    """
    Display ANSI artwork directly to the console without scrolling.

    Args:
        context: The current SSHContext.
        path: The path of the file to display.
        encoding: The encoding of the file to display.
    """

    await scroll_art(context, path, encoding, 0.0)
