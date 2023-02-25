"art module"

# type checking
from typing import Optional, Union

# stdlib
import asyncio as aio
from os.path import exists, isfile

# 3rd party
import aiofiles
from blessed.keyboard import Keystroke
from blessed.sequences import SequenceTextWrapper

# local
from ..context import Context


async def show_art(
    cx: Context,
    filename: str,
    delay=0.2,
    dismissable=True,
    preload=0,
    maxwidth: Optional[int] = None,
    center=False,
    encoding="cp437",
) -> Union[Keystroke, None]:
    """
    Display artwork from given filename with given delay between rows of
    output.

    :param cx: The current context
    :param filename: The filename to load
    :param delay: Delay (in seconds) between rows of output
    :param dismissable: If the display can be prematurely ended by keypress
    :param preload: Number of rows to show immediately without delay
        (0 for term height - 1, None for no preload)
    :param maxwidth: The maximum number of columns to display
    :param center: True to center output
    :param encoding: The encoding to use for output
    :returns: The keypress and prematurely ended the display, if any
    """

    def newline():
        cx.echo(f"{cx.term.normal}\r\n")

    if maxwidth is None or maxwidth > cx.term.width:
        maxwidth = cx.term.width - 1

    if not (exists(filename) and isfile(filename)):
        raise FileNotFoundError(f"Could not find {filename}")

    if preload is not None and preload <= 0:
        preload = cx.term.height - 1

    center_pos = (
        0 if not center else min(0, (cx.term.width // 2) - (maxwidth // 2))
    )
    row = 0

    async with aiofiles.open(filename, "r", encoding=encoding) as f:
        if cx.encoding != "utf-8":
            encoding = None

        wrapper = SequenceTextWrapper(
            min(maxwidth, cx.term.width - 1), cx.term  # type: ignore
        )

        for line in await f.readlines():
            # \x1a is the EOF character, used to delimit SAUCE from the artwork
            if "\x1a" in line:
                break

            output = []

            if center_pos > 0:
                output.append(cx.term.move_x(center_pos))

            wrapped = wrapper.wrap(line)
            output.append(wrapped[0] if wrapped else line)
            cx.echo("".join(output))
            row += 1

            if preload is not None and row < preload:
                newline()
                continue

            if delay is not None and delay > 0:
                if dismissable:
                    ks: Keystroke = await cx.term.inkey(timeout=delay)

                    if ks.code is not None:
                        newline()
                        return ks
                else:
                    await aio.sleep(delay)

            newline()
