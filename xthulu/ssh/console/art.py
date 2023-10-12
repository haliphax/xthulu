"""Artwork display"""

# stdlib
from asyncio import QueueEmpty, sleep
from re import Match, sub

# 3rd party
import aiofiles as aiof
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

            try:
                self.context.input.get_nowait()
                break
            except QueueEmpty:
                await sleep(0.1)
        else:
            await sleep(1)

        self.exit()

    async def on_key(self, _: events.Key):
        self.exit()


def _replace_cuf(match: Match[str]):
    return " " * int(match.group(1))


def normalize_ansi(text: str):
    """Replace CUF sequences with spaces."""

    return sub(FIND_CUF_REGEX, _replace_cuf, text)


async def load_art(path: str, encoding="cp437"):
    """Load normalized, properly-encoded artwork files."""

    async with aiof.open(path, encoding=encoding) as f:
        artwork = [normalize_ansi(line) for line in await f.readlines()]

    return artwork


async def scroll_art_app(
    context: SSHContext, path: str, encoding="cp437", delay=0.1
):
    """Display ANSI artwork in a scrolling Log panel."""

    if context.encoding != "utf-8":
        encoding = context.encoding

    artwork = await load_art(path, encoding)
    await ArtLog(context, artwork, delay).run_async()


async def scroll_art(
    context: SSHContext, path: str, encoding="cp437", delay=0.1
):
    """Display ANSI artwork directly to the console."""

    if context.encoding != "utf-8":
        encoding = context.encoding

    artwork = await load_art(path, encoding)

    # show entire piece immediately if shorter than terminal
    if context.term.height >= len(artwork):
        context.term.out(*artwork)
        return

    for line in artwork:
        context.term.out(
            line,
            end="",
            highlight=False,
        )

        try:
            context.input.get_nowait()
            break
        except QueueEmpty:
            await sleep(delay)
    else:
        await sleep(1)


async def show_art(context: SSHContext, path: str, encoding="cp437"):
    """Display ANSI artwork directly to the console without scrolling."""

    if context.encoding != "utf-8":
        encoding = context.encoding

    context.term.out(*(await load_art(path, encoding)))
