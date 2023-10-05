"""art module"""

# stdlib
from asyncio import sleep
from os.path import exists, isfile
import re

# 3rd party
from aiofiles import open
from blessed.keyboard import Keystroke
from blessed.sequences import SequenceTextWrapper

# local
from ..context import SSHContext


async def show_art(
    cx: SSHContext,
    filename: str,
    delay=0.125,
    dismissable=True,
    preload=0,
    maxwidth: int | None = None,
    center=False,
    encoding="cp437",
) -> Keystroke | None:
    """
    Display artwork from given filename with given delay between rows of
    output.

    Args:
        cx: The current context.
        filename: The filename to load.
        delay: Delay (in seconds) between rows of output.
        dismissable: If the display can be prematurely ended by keypress.
        preload: Number of rows to show immediately without delay
            (0 for term height - 1, None for no preload).
        maxwidth: The maximum number of columns to display.
        center: True to center output.
        encoding: The encoding to use for output.

    Returns:
        The keypress and prematurely ended the display, if any.
    """

    def newline():
        cx.echo(f"{cx.term.normal}\r\n")

    if maxwidth is None or maxwidth > cx.term.width - 1:
        maxwidth = cx.term.width - 1

    assert maxwidth is not None

    if not (exists(filename) and isfile(filename)):
        raise FileNotFoundError(f"Could not find {filename}")

    if preload is not None and preload <= 0:
        preload = cx.term.height - 1

    file_lines: list[str]

    async with open(filename, "r", encoding=encoding) as f:
        file_lines = await f.readlines()

    lines: list[str] = []
    wrapper = SequenceTextWrapper(maxwidth, cx.term)  # type: ignore
    longest_line = 0

    # \x1a is the EOF character, used to delimit SAUCE from the artwork
    for line in [re.sub(r"\r|\n|\x1a.*", "", l) for l in file_lines]:
        # replace CUF sequences with spaces to avoid loss of background
        # color when a CUF sequence would wrap
        normalized = re.sub(
            r"\x1b\[(\d+)C", lambda x: " " * int(x.group(1)), line
        )
        # wrap to maximum width and discard excess
        wrapped = wrapper.wrap(normalized)
        did_wrap = len(wrapped) > 1
        first = wrapped[0] if did_wrap else normalized
        lines.append(first)

        # calculate longest line length for centering
        if center and longest_line < maxwidth:
            if did_wrap:
                # if this line wrapped, we know it's at least maxwidth
                longest_line = maxwidth

            else:
                # strip sequences to get true length
                stripped = re.sub(r"\x1b\[[;0-9]+m", "", first)
                strlen = len(stripped)

                if strlen > longest_line:
                    longest_line = strlen

    center_pos = (
        0 if not center else max(0, (cx.term.width // 2) - (longest_line // 2))
    )
    row = 0

    for line in lines:
        if center_pos > 0:
            cx.echo(cx.term.move_right(center_pos))

        cx.echo(line)
        row += 1

        if preload is not None and row < preload:
            newline()

            continue

        if delay is not None and delay > 0:
            if cx.events.get("resize"):
                newline()

                return

            if dismissable:
                ks: Keystroke = await cx.term.inkey(timeout=delay)

                if ks.code is not None:
                    newline()

                    return ks

            else:
                await sleep(delay)

        newline()
