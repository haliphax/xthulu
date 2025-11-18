"""Artwork display"""

# stdlib
from re import Match, sub

# 3rd party
import aiofiles as aiof
from rich.text import Text

# local
from ..context import SSHContext

FIND_BOLD_REGEX = r"(\x1b\[(?:\d+;)?)30m"
FIND_CUF_REGEX = r"\x1b\[(\d+)?C"


def _replace_bold(match: Match[str]) -> str:
    return f"{match.group(1)}90m"


def _replace_cuf(match: Match[str]) -> str:
    how_many = int(match.group(1) or 1)

    if how_many < 1:
        how_many = 1

    return " " * how_many


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


async def scroll_art(
    context: SSHContext,
    path: str,
    encoding="cp437",
    delay=0.1,
    bold_as_bright=True,
) -> bytes | None:
    """
    Display ANSI artwork directly to the console.

    Args:
        context: The current `xthulu.ssh.context.SSHContext`.
        path: The path of the file to display.
        encoding: The encoding of the file to display.
        delay: The delay (in seconds) between displaying each line.
        bold_as_bright: Render "bold" as "bright" (e.g. for classic DOS ANSI).

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
        if bold_as_bright:
            line = sub(FIND_BOLD_REGEX, _replace_bold, line)

        processed = Text.from_ansi(line, overflow="crop", no_wrap=True, end="")
        context.console.print(
            processed,
            emoji=False,
            end="\n",
            height=1,
            highlight=False,
            markup=False,
            overflow="ignore",
            no_wrap=True,
        )

        if delay <= 0:
            continue

        key = await context.inkey(timeout=delay)

        if key:
            return key

    return None


async def show_art(context: SSHContext, path: str, encoding="cp437") -> None:
    """
    Display ANSI artwork directly to the console without scrolling.

    Args:
        context: The current `xthulu.ssh.context.SSHContext`.
        path: The path of the file to display.
        encoding: The encoding of the file to display.
    """

    await scroll_art(context, path, encoding, 0.0)
