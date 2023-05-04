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
    MODIFIERS,
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


class GraphemeBuffer(list[Grapheme | None]):

    """
    A contiguous segment of cells for display on the console, each of which is
    either a `Grapheme` instance or `None`. A value of `None` should denote that
    the cell is occupied by the remainder of the previous `Grapheme` (i.e. the
    previous `Grapheme` has a `width` value greater than 1).
    """

    def __add__(self, other: GraphemeBuffer | str | None):
        updated = self.copy()

        if other is None:
            return GraphemeBuffer(updated)

        if isinstance(other, str):
            other = GraphemeBuffer.from_str(other)

        for g in other:
            updated.append(g)

        return GraphemeBuffer(updated)

    def __iadd__(self, other: GraphemeBuffer | str | None):
        if other is None:
            return

        if isinstance(other, str):
            other = GraphemeBuffer.from_str(other)

        for g in other:
            self.append(g)

        return self

    def __repr__(self):
        return f"GraphemeBuffer({len(self)})"

    def __setitem__(self, key: int, value: Grapheme | str | None):
        if isinstance(value, str):
            value = GraphemeBuffer.from_str(value)[0]

        self[key] = value

    def __str__(self):
        return "".join(str(g) if g else "" for g in self)

    @property
    def count(self):
        """The total number of `Grapheme` objects, excluding `None` values."""

        return sum([1 if g else 0 for g in self])

    @property
    def raw(self):
        """Console output as a `str` without forced-width adjustments."""

        return "".join(g.raw if g else "" for g in self)

    def _strip(self, lstrip: bool = False) -> GraphemeBuffer:
        length = len(self)

        if length == 0:
            return GraphemeBuffer()

        idx = -1 if lstrip else 0
        limit = length + idx
        step = 1 if lstrip else -1
        grapheme: Grapheme | None = None
        discard = set((" ", "\n"))
        absidx = 0

        while (grapheme is None or grapheme.char in discard) and absidx < limit:
            idx += step
            absidx = abs(idx)
            grapheme = self[idx]

        if not grapheme:
            log_debug("empty after strip")
            return GraphemeBuffer()

        if not lstrip:
            idx -= step * grapheme.width

        if idx == 0:
            return GraphemeBuffer(self.copy())

        log_debug(f"stripped: {idx}")
        return GraphemeBuffer(self[idx:] if lstrip else self[:idx])

    def lstrip(self):
        """Trim leading spaces/newlines."""

        return self._strip(True)

    def rstrip(self):
        """Trim trailing spaces/newlines."""

        return self._strip()

    def strip(self):
        """Trim leading and trailing spaces/newlines."""

        return self._strip()._strip(True)

    def split(self, separator: Grapheme | str):
        """
        Split the segment into smaller segments, separated by `separator`.

        Args:
            separator: The `Grapheme` or `str` to use for tokenizing.

        Returns:
            A list of `ConsoleString` instances.
        """

        is_grapheme = isinstance(separator, Grapheme)
        result: list[GraphemeBuffer] = []
        segment = GraphemeBuffer()

        for g in self:
            if g and (
                (is_grapheme and g == separator)
                or (not is_grapheme and g.char == separator)
            ):
                result.append(segment)
                segment = GraphemeBuffer()
                continue

            segment.append(g)

        if len(segment):
            result.append(segment)

        return result

    @classmethod
    def from_str(cls, string: str) -> GraphemeBuffer:
        """
        Split a string into (potentially clustered) graphemes.

        Args:
            string: The string to parse.

        Returns:
            A `ConsoleString` instance representing the input string.
        """

        def _append_cell(cell: Grapheme, cells: GraphemeBuffer):
            log_debug(f"appending {cell!r}")
            cells.append(cell)

            # pad cells following wide graphemes with `None` filler
            if cell.width > 1:
                for _ in range(0, cell.width - 1):
                    cells.append(None)

            return Grapheme()

        cell = Grapheme()
        cells = GraphemeBuffer()
        joined = False
        was_emoji = False

        for c in string:
            assert cell

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
                    idx = -1
                    prev: Grapheme | None = None

                    while prev is None and -idx <= len(cells):
                        prev = cells[idx]
                        idx -= 1

                    if prev is None:
                        log_debug("walk ended unexpectedly")
                    else:
                        prev.mods.append(c)
                        cell = Grapheme()
                else:
                    log_debug("unexpected combining character")

                continue

            if c in VARIATION_SELECTORS:
                log_debug(f"variation selector: 0x{ord(c):04X}")

                if cell.char == "":
                    cell = cells.pop()
                    assert cell

                if c == EMOJI_VS:
                    log_debug("emoji VS")
                    was_emoji = True

                    if FORCE_EVS_WIDE and cell.width < 2:
                        log_debug("forced wide")
                        cell.width = 2
                        cell.force_width = True

                cell.mods.append(c)
                continue

            if c in MODIFIERS:
                log_debug(f"base modifier: {c!r}")

                if cell.char != "":
                    cell.mods.append(c)
                else:
                    cell.char = c

                if not is_emoji(cell.raw):
                    # separate modifier from emoji if invalid
                    log_debug(f"invalid base: {cell!r}")

                    if cell.mods:
                        cell.mods.pop()

                    cell.mods.append(ZWNJ)
                    cell = _append_cell(cell, cells)
                else:
                    was_emoji = True
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
                idx = -1
                prev: Grapheme | None = None

                while prev is None and -idx <= len(cells):
                    prev = cells[idx]
                    idx -= 1

                if prev is None:
                    log_debug("walk ended unexpectedly")
                elif not is_emoji(str(prev).rstrip().rstrip(EMOJI_VS)):
                    log_debug(f"invalid emoji: {prev!r}")
                    # strip all but base emoji character if invalid
                    prev.mods.clear()

            was_emoji = False

            if wcswidth(c) < 1:
                hexstr = f"0x{ord(c):04X}"

                if c not in VALID_ZWC:
                    log_debug(f"stripping ZWC: {hexstr}")
                    continue

                log_debug(f"ZWC: {hexstr}")

            cell.char = c
            cell = _append_cell(cell, cells)

        return cells
