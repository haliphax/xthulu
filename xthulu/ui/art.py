"art module"

# stdlib
import asyncio as aio
from os.path import exists, isfile
from re import sub
from typing import Union
# 3rd party
import aiofiles as aiof
from blessed.keyboard import Keystroke
# local
from ..context import Context


async def show_art(cx: Context, filename: str, delay=0.2,
                   dismissable=True, preload=0) -> Union[Keystroke, None]:
    """
    Display artwork from given filename with given delay between lines of
    output.

    :param term: The terminal to echo to
    :param filename: The filename to load
    :param delay: Delay (in seconds) between lines of output
    :param dismissable: If the display can be prematurely ended by keypress
    :param preload: Number of lines to show immediately without delay
        (0 for term height - 1, None for no preload)
    :returns: The keypress and prematurely ended the display, if any
    """

    if not (exists(filename) and isfile(filename)):
        raise FileNotFoundError(f'Could not find {filename}')

    if preload <= 0:
        preload = cx.term.height - 1

    first = True
    count = 0

    async with aiof.open(filename, 'r') as f:
        for line in await f.readlines():
            if not first:
                cx.echo('\r\n')

            count += 1
            first = False
            line = sub('\r|\n', '', line)
            cx.echo(line)

            if preload is not None and count < preload:
                continue

            if delay is not None and delay > 0:
                if dismissable:
                    ks: Keystroke = await cx.term.inkey(delay)

                    if ks.code is not None:
                        return ks
                else:
                    await aio.sleep(delay)

    cx.echo('\r\n')
