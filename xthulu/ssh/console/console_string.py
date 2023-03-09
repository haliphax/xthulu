"""ConsoleString class"""

# type checking
from __future__ import annotations

# stdlib
import unicodedata

# 3rd party
from emoji import is_emoji
from wcwidth import wcswidth

# local
from ...configuration import get_config
from ...logger import log
from .constants import (
    ASSUME_WIDE,
    EMOJI_VS,
    FORCE_EVS_WIDE,
    SKIN_TONES,
    VALID_ZWC,
    VARIATION_SELECTORS,
    ZWJ,
    ZWNJ,
)
from .grapheme import Grapheme

DEBUG_CONSOLE = get_config("debug.console", False)


def log_debug(x):
    if DEBUG_CONSOLE:
        log.debug(x)


class ConsoleString(list[Grapheme | None]):

    """
    A contiguous segment of cells for display on the console, each of which is
    either a `Grapheme` instance or `None`. A value of `None` should denote that
    the cell is occupied by the remainder of the previous `Grapheme` (i.e. the
    previous `Grapheme` has a `width` value greater than 1).
    """

    def split(self, separator: Grapheme | str):
        """
        Split the segment into smaller segments, separated by `separator`.

        Args:
            separator: The `Grapheme` or `str` to use for tokenizing.

        Returns:
            A list of `ConsoleString` instances.
        """

        is_grapheme = isinstance(separator, Grapheme)
        result: list[ConsoleString] = []
        segment = ConsoleString()

        for g in self:
            if g and (
                (is_grapheme and g == separator)
                or (not is_grapheme and g.char == separator)
            ):
                result.append(segment)
                segment = ConsoleString()
                continue

            segment.append(g)

        if len(segment):
            result.append(segment)

        return result

    @classmethod
    def from_str(cls, string: str) -> ConsoleString:
        """
        Split a string into (potentially clustered) graphemes.

        Args:
            string: The string to parse.

        Returns:
            A `ConsoleString` instance representing the input string.
        """

        def _append_cell(cell: Grapheme, cells: ConsoleString):
            cells.append(cell)
            return Grapheme()

        cell = Grapheme()
        cells = ConsoleString()
        joined = False
        was_emoji = False

        for c in string:
            assert cell is not None

            if c == ZWJ:
                if was_emoji:
                    log_debug("ZWJ")
                    cell.mods.append(c)
                    joined = True
                else:
                    log_debug("unexpected ZWJ")

                continue

            if c == ZWNJ:
                joined = False

                if cell.char != "":
                    log_debug(f"ZWNJ{'; end emoji' if was_emoji else ''}")
                    cell.mods.append(c)
                    was_emoji = False
                else:
                    log_debug("unexpected ZWNJ")

                continue

            if unicodedata.combining(c) != 0:
                if cells:
                    log_debug(f"combining character: {'o' + c!r}")
                    cell = cells.pop()
                    assert cell is not None
                    cell.mods.append(c)
                else:
                    log_debug("unexpected combining character")

                continue

            if c in VARIATION_SELECTORS:
                if cell.char != "":
                    if c == EMOJI_VS:
                        if was_emoji:
                            log_debug("emoji variation selector")
                            cell.mods.append(c)

                            if FORCE_EVS_WIDE and cell.width < 2:
                                log_debug("forced wide")
                                cell.width = 2
                                cell.force_width = True
                        else:
                            log_debug("unexpected emoji variation selector")
                    else:
                        log_debug(f"variation selector: {c!r}")
                        cell.mods.append(c)
                else:
                    log_debug("unexpected variation selector")

                continue

            if c in SKIN_TONES and was_emoji:
                log_debug(f"skin tone: {c!r}")
                cell.mods.append(c)

                if not is_emoji(cell.raw):
                    # separate skin tone modifier from emoji if invalid
                    log_debug(f"invalid base: {cell!r}")
                    cell.mods.pop()
                    cell.mods.append(ZWNJ)
                    cell = _append_cell(cell, cells)
                else:
                    continue

            if joined:
                log_debug(f"joining: {c!r}")
                cell.mods += c
                joined = False
                continue

            if cell.char != "":
                cell = _append_cell(cell, cells)

            if unicodedata.east_asian_width(c) == "W":
                log_debug("wide")
                cell.width = 2
            else:
                cell.width = wcswidth(c)

            # assume the terminal will cause a problematic visual column offset
            # when displaying emoji that are (incorrectly) labeled as Narrow
            if ASSUME_WIDE and was_emoji and cell.width < 2:
                log_debug("assumed wide")
                cell.width = 2
                cell.force_width = True

            if is_emoji(c):
                log_debug(f"emoji: {c!r}")
                cell.char = c
                was_emoji = True
                continue

            if was_emoji:
                log_debug("end emoji")
                last = cells[-1]
                assert last is not None

                if not is_emoji(str(last).rstrip().rstrip(EMOJI_VS)):
                    log_debug(f"invalid emoji: {last!r}")
                    # strip all but base emoji character if invalid
                    last.mods.clear()

            was_emoji = False

            if wcswidth(c) < 1:
                hexstr = "0x%04X" % ord(c)

                if c not in VALID_ZWC:
                    log_debug(f"stripping ZWC: {hexstr}")
                    continue

                log_debug(f"ZWC: {hexstr}")

            cell.char = c
            cell = _append_cell(cell, cells)

        return cells
