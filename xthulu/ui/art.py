"art module"

# stdlib
import asyncio as aio
from os.path import exists, isfile
import re
from typing import Union
# 3rd party
import aiofiles
from blessed.keyboard import Keystroke
# local
from ..context import Context


async def show_art(cx: Context, filename: str, delay=0.2,
                   dismissable=True, preload=0, maxwidth=80, center=False,
                   encoding='cp437') \
        -> Union[Keystroke, None]:
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

    def done():
        cx.echo(f'{cx.term.normal}\r\n')

    async def do_delay() -> Union[Keystroke, None]:
        if delay is None or delay <= 0:
            return

        if dismissable:
            ks: Keystroke = await cx.term.inkey(timeout=delay)

            if ks.code is not None:
                return ks
        else:
            await aio.sleep(delay)

    if maxwidth > cx.term.width:
        maxwidth = cx.term.width

    if not (exists(filename) and isfile(filename)):
        raise FileNotFoundError(f'Could not find {filename}')

    if preload is not None and preload <= 0:
        preload = cx.term.height - 1

    center_pos = 0 if not center \
        else max(0, (cx.term.width // 2) - (maxwidth // 2))
    first = True
    row = 0
    lastcolor = ''

    async with aiofiles.open(filename, 'r', encoding=encoding) as f:
        for line in await f.readlines():
            out = []

            if not first:
                out.append(f'{cx.term.normal}\r\n')

            if center_pos > 0:
                out.append(cx.term.move_x(center_pos))

            cx.echo(''.join(out))

            col = 0
            row += 1
            first = False
            line = re.sub(r'\r|\n|\x1a.*', '', line)
            out = []
            seqs = cx.term.split_seqs(line)
            ignore = False

            for seq in seqs:
                if ignore:
                    ignore = False

                    continue

                if seq[0] == '\x1b':
                    if seq[-1] == 'C':
                        spaces = re.findall(r'\d+', seq)

                        if len(spaces) == 0:
                            col += 1
                        else:
                            col += int(spaces[0])

                        ignore = True
                    elif seq[-1] == 'm':
                        colors = re.findall(r'4[0-7]', seq)

                        for c in colors:
                            if c == '40':
                                c = 0

                            lastcolor = f'\x1b[{c}m'

                    out.append(seq)

                    continue

                strlen = len(seq)

                while True:
                    fit = maxwidth - col

                    if strlen > fit:
                        out.append(seq[0:fit])
                        seq = seq[fit:]
                        strlen = len(seq)
                        cx.echo(''.join(out), encoding=encoding)
                        out.clear()
                        row += 1
                        col = 0

                        if cx.term.width > maxwidth:
                            out.append(f'{cx.term.normal}\r\n')

                            if center_pos > 0:
                                out.append(cx.term.move_right(center_pos))

                            out.append(lastcolor)
                            cx.echo(''.join(out))
                            out.clear()

                        if preload is not None and row < preload:
                            continue

                        ks = await do_delay()

                        if ks is not None and ks.code is not None:
                            done()

                            return ks
                    else:
                        break

                out.append(seq)
                col += strlen

            cx.echo(''.join(out), encoding=encoding)

            if preload is not None and row < preload:
                continue

            ks = await do_delay()

            if ks is not None and ks.code is not None:
                done()

                return ks

    done()
