"""Block editor"""

# type checking
from typing import Callable

# stdlib
from re import findall, match, sub

# 3rd party
from blessed.keyboard import Keystroke
from wcwidth import wcswidth

# local
from ....logger import log
from ...terminal.proxy_terminal import ProxyTerminal

# grapheme cluster modifiers

ZWJ = "\u200d"
"""Zero-width join; next grapheme modifies the cluster"""

VARIATION = r"[\ufe00-\ufe0f]"
"""Variation; previous grapheme modifies the cluster"""

SKIN_TONE = r"[\U0001f3fb-\U0001f3ff]"
"""Skin tone modifiers; modifies previous grapheme (no join sequence)"""

MODIFIERS = rf"{VARIATION}|{SKIN_TONE}|{ZWJ}"
"""Grapheme modifiers commonly searched for while parsing"""


def realwidth(ucs: str):
    return wcswidth(sub(rf".{VARIATION}|(?=.){SKIN_TONE}|{ZWJ}.", "", ucs))


class BlockEditor:

    """Block editor (multiple lines)"""

    value = []
    """Editor text"""

    limit = [0, 0]
    """Text length limit (width, height)"""

    corner = [None, None]
    """Top-left corner of editor on screen (x, y)"""

    cursor = [0, 0]
    """Cursor offset from top-left corner on screen (x, y)"""

    pos = [0, 0]
    """Position within corpus of corner of editor (x, y)"""

    # internals
    _color_str = "bright_white_on_blue"
    _color: Callable[[str], str] | None = None
    # used for tracking position re: visible sequence, not raw byte offset
    _cursor_offset = 0

    def __init__(self, term: ProxyTerminal, rows: int, columns: int, **kwargs):
        self.term = term
        """Terminal to use for sequences"""

        self.rows = rows
        """Height in rows"""

        self.columns = columns
        """Width in columns"""

        if "value" not in kwargs:
            self.value = [""] * rows

        if "color" in kwargs:
            self._color_str = kwargs["color"]
            del kwargs["color"]

        for k in kwargs:
            setattr(self, k, kwargs[k])

        self._color = getattr(term, self._color_str)
        strlen = 0

        if "pos" not in kwargs:
            for i in range(max(0, len(self.value) - self.rows)):
                if len(self.value[i]) > 0:
                    self.pos[1] = i

            strlen = realwidth(self.value[self.pos[1]])
            self.pos[0] = max(0, strlen - self.columns)

        if "cursor" not in kwargs:
            if strlen == 0:
                strlen = realwidth(self.value[self.pos[1]])

            self.cursor[0] = min(self.columns - 1, max(0, strlen))
            self.cursor[1] = min(self.rows - 1, max(0, len(self.value) - 1))

        log.debug(f"corner: {self.corner}")
        log.debug(f"pos: {self.pos}")
        log.debug(f"cursor: {self.cursor}")

    @property
    def _char_behind(self):
        try:
            return self.value[self.pos[1] + self.cursor[1]][
                self.pos[0] + self.cursor[0] - 1
            ]
        except IndexError:
            return ""

    @property
    def _char_under(self):
        try:
            return self.value[self.pos[1] + self.cursor[1]][
                self.pos[0] + self.cursor[0]
            ]
        except IndexError:
            return ""

    @property
    def color(self) -> Callable:
        """
        Color property; setting it also sets the internal Terminal callable.
        """

        return getattr(self.term, self._color_str)

    @color.setter
    def color(self, val):
        self._color_str = val
        self._color = getattr(self.term, val)

    @property
    def at_end(self) -> bool:
        """Whether the cursor is at the end of the editor."""

        if self.limit[0] == 0:
            return False

        return (
            self.cursor[0] >= self.columns - 1
            and realwidth(self.value[self.pos[1]]) >= self.limit[0]
        )

    @property
    def edge_diff(self) -> int:
        """How far the cursor is from the edge of the current row."""

        strlen = realwidth(self.value[self.cursor[1] + self.pos[1]])

        return self.pos[0] + self.cursor[0] - strlen

    def redraw(self, cursor=True, anchor=True) -> str:
        """
        Output sequence to redraw editor.

        Args:
            cursor: Redraw cursor position as well.
            anchor: Reset anchor position as well.

        Returns:
            The output string to redraw the editor/cursor.
        """

        out = ""
        left = self.pos[0]
        top = self.pos[1]
        travel = 0

        if anchor:
            out += self.reset_anchor()

        for i in range(self.rows):
            if i > 0:
                out += "\r\n"
                travel += 1

            if self.corner[0] is not None:
                out += self.term.move_x(self.corner[0])

            text = self.value[top + i][left : left + self.columns]
            out += self.color(text)
            out += self.color(" " * (self.columns - realwidth(text)))
            out += self.term.move_left(self.columns)

        log.debug("redrawing editor")

        if cursor:
            if travel > 0:
                out += self.term.move_up(travel)

            out += self.redraw_cursor()

        return out

    def redraw_cursor(self) -> str:
        """
        Output sequence to restore cursor position; assumes cursor is already
        located at top-left of editor if self.corner is unset.

        Returns:
            The output sequence to redraw the cursor.
        """

        out = ""

        # move cursor back to top left before adjusting to self.cursor offset
        if self.corner[0] is not None:
            out += self.term.move_x(self.corner[0])

        if self.corner[1] is not None:
            out += self.term.move_y(self.corner[1])

        # adjust offset
        if self.cursor[0] > 0:
            out += self.term.move_right(self.cursor[0])

        if self.cursor[1] > 0:
            out += self.term.move_down(self.cursor[1])

        log.debug("redrawing cursor")

        return out

    def reset_anchor(self) -> str:
        """
        Assuming the cursor has not moved since the editor was responsible for
        it, this will reset the on-screen cursor to the top-left corner of the
        editor.

        Returns:
            The output sequence to reset the anchor.
        """

        out = ""

        if self.cursor[0] > 0:
            out += self.term.move_left(self.cursor[0])

        if self.cursor[1] > 0:
            out += self.term.move_up(self.cursor[1])

        log.debug("resetting anchor")

        return out

    def reset(self):
        """Reset the editor's value, cursor, and offset position."""

        self.cursor = [0, 0]
        self.pos = [0, 0]
        self.value = [""] * self.rows

    @property
    def _row_vars(self):
        row = self.value[self.pos[1] + self.cursor[1]]
        dist = 0
        offset = 0
        zwj = False
        lastw = 0

        for ucs in row:
            if zwj:
                zwj = False
                log.debug(f"skipping {ucs!r} due to zwj")
                continue

            w = realwidth(ucs)
            log.debug(f"ucs: {ucs!r}, width: {w}")

            if match(VARIATION, ucs):
                offset += 1
                log.debug(f"offsetting variation: {ucs!r}")
                dist -= lastw
            elif match(ZWJ, ucs):
                offset += 1
                log.debug(f"offsetting zwj: {ucs!r}")
                zwj = True
            elif ucs.encode("utf8").startswith(b"\xf0\x9f\x8f"):
                offset += 1
                log.debug(f"offsetting skin tone: {ucs!r}")
            else:
                log.debug(f"width: {w}")
                dist += w

            if dist > self.pos[0] + self.cursor[0]:
                break

            lastw = w

        log.debug(f"dist: {dist}")
        log.debug(f"offset: {offset}")
        self._cursor_offset = offset
        before = row[: self.pos[0] + self.cursor[0] + self._cursor_offset]
        after = row[self.pos[0] + self.cursor[0] + self._cursor_offset :]

        return row, before, after

    def _kp_backspace(self) -> str:
        log.debug(self._cursor_offset)
        row, before, after = self._row_vars
        log.debug((row, before, after))
        log.debug(self._cursor_offset)

        if self.pos[0] <= 0 and self.cursor[0] == 0:
            log.debug("at start of line, nothing to backspace")
            return ""

        shift = False
        offset = 0
        behind = before

        while True:
            modifiers = findall(MODIFIERS, behind)

            for m in modifiers:
                encoded = m.encode("utf8")

                if encoded.startswith(b"\xf0\x9f\x8f"):
                    log.debug(f"skin tone: {m}")
                    offset += 2
                elif m == ZWJ:
                    log.debug(f"zwj: {m!r}")
                    offset += 2
                else:
                    log.debug(f"variation: {m!r}")
                    offset += 2

            if match(r".*(?!.{VARIATION}|{ZWJ}.)?$", behind):
                log.debug("previous char is a variation/zwj")
                offset += 1
            elif match(SKIN_TONE, behind):
                log.debug("previous char is skin tone modifier")
                offset += 1
            else:
                break

            behind = before[-offset]

        dist = wcswidth(behind)

        self.value[self.pos[1] + self.cursor[1]] = before[: -1 - offset] + after
        out = ""

        after = after[: min(len(after), self.columns - self.cursor[0])]
        total = dist + offset

        if self.cursor[0] < dist:
            self.pos[0] = max(0, self.pos[0] - dist)
            self.cursor[0] = 0
            shift = True
        else:
            after += " " * total

            if total > 0:
                out += self.term.move_left(total)

            self.cursor[0] -= dist
            self._cursor_offset -= offset

        if shift:
            out = self.redraw()
        else:
            out += self.color(after)

            if total > 0:
                out += self.term.move_left(total)

        log.debug(
            f"backspace {self.pos} {self.cursor} "
            f"{self.value[self.pos[1] + self.cursor[1]]!r}"
        )

        return out

    def _kp_delete(self) -> str:
        _, before, after = self._row_vars

        if self.pos[0] >= realwidth(self.value[self.pos[1]]):
            log.debug("at end of line, nothing to delete")
            return ""

        after = after[1:]
        dist = realwidth(after)
        self.value[self.pos[1] + self.cursor[1]] = before + after
        after = after[: self.columns - self.cursor[0]]
        out = ""

        if self.cursor[0] + dist <= self.columns - 1:
            after += " " * (dist + 1)
            out += self.term.move_left(dist + 1)

        log.debug(f'delete "{self.value[self.pos[1] + self.cursor[1]]}"')

        return self.color(
            after + (self.term.move_left(dist) if dist > 0 else "") + out
        )

    def _horizontal(self, distance: int) -> str:
        """
        Horizontal movement helper method; handles shifting visible area.

        Args:
            distance: The distance to travel. Negative = left, positive = right.

        Returns:
            The output sequence for updating the screen.
        """

        if distance == 0:
            return ""

        row, before, after = self._row_vars
        log.debug((row, before, after))
        strlen = realwidth(row)
        blen = len(before)
        log.debug(f"before: {blen}")

        if distance == 1 and after:
            distance = realwidth(after[0])

        elif distance == -1 and blen > 1:
            idx = -1

            while -idx < blen:
                check = before[idx]
                log.debug(f"check: {check!r}")

                if match(VARIATION, check):
                    log.debug("variation; skipping")
                    idx -= 1
                elif match(SKIN_TONE, check):
                    log.debug("skin tone; skipping")
                elif check == ZWJ:
                    log.debug("zwj; skipping")
                elif -idx < blen - 1 and before[idx - 1] == ZWJ:
                    log.debug("zero-joined; skipping")
                    idx -= 1
                else:
                    break

                idx -= 1

            distance = -realwidth(before[idx])
            log.debug(f"distance: {distance}")

        if distance < 0 and self.cursor[0] <= 0 and self.pos[0] <= 0:
            log.debug("already at start of line")

            return ""

        if distance > 0 and self.edge_diff >= 0:
            log.debug("already at end of line")

            return ""

        shift = False
        move: Callable[..., str]

        new_cursor = self.cursor[0] + distance
        abs_distance = abs(distance)

        if distance < 0:
            if new_cursor < 0:
                log.debug("shifting visible area left")
                self.pos[0] = max(
                    0, self.pos[0] + self.cursor[0] - abs_distance
                )
                new_cursor = 0
                shift = True

            move = self.term.move_left

        else:
            if new_cursor > self.columns - 1:
                log.debug("shifting visible area right")
                self.pos[0] = min(
                    strlen - self.columns + 1, self.pos[0] + abs_distance
                )
                new_cursor = self.columns - 1
                shift = True

            move = self.term.move_right

        out: list[str] = [move(abs(self.cursor[0] - new_cursor))]
        self.cursor[0] = new_cursor

        if shift:
            out.append(self.redraw())

        log.debug(
            f"{'left' if distance < 0 else 'right'} {self.pos} {self.cursor} "
            f"{self._char_under}"
        )

        return "".join(out)

    def _vertical(self, distance: int) -> str:
        """
        Vertical movement helper method; handles shifting visible area and
        snapping the cursor to the edge of the destination row's text.

        Args:
            distance: The distance to travel. Negative = up, positive = down.

        Returns:
            The output sequence for updating the screen.
        """

        if distance == 0:
            return ""

        if distance < 0 and self.cursor[1] <= 0 and self.pos[1] <= 0:
            log.debug("already at start of editor")

            return ""

        if distance > 0 and self.pos[1] + self.cursor[1] >= len(self.value) - 1:
            log.debug("already at end of editor")

            return ""

        snap_to_edge = self.edge_diff >= 0
        shift = False
        vallen = len(self.value)
        clamp_low = -(self.pos[1] + self.cursor[1])
        clamp_high = vallen - self.pos[1] - self.cursor[1]
        log.debug(f"distance clamp: {clamp_low} - {clamp_high}")
        distance = min(clamp_high, max(clamp_low, distance))
        new_cursor = self.cursor[1] + distance
        log.debug(f"new cursor: {new_cursor}")
        out = []

        if distance < 0:
            if new_cursor < 0:
                log.debug("shifting visible area up")
                new_cursor = 0
                shift = True

            move = self.term.move_up

        else:
            if new_cursor >= self.rows:
                log.debug("shifting visible area down")
                new_cursor = self.rows - 1
                shift = True

            move = self.term.move_down

        if shift:
            self.pos[1] = max(
                0,
                min(self.pos[1] + distance, vallen - self.rows),
            )

        log.debug(f"clamped new cursor: {new_cursor}")
        cursor_shift = abs(self.cursor[1] - new_cursor)
        log.debug(f"cursor shift: {cursor_shift}")

        if shift and cursor_shift > 0:
            out.append(move(cursor_shift))

        self.cursor[1] = new_cursor
        diff = self.edge_diff

        if not snap_to_edge and diff > 0:
            log.debug("past end of line")
            snap_to_edge = True

        if snap_to_edge:
            log.debug("snapping to edge")
            self.cursor[0] -= diff

            if self.cursor[0] < 0 or self.cursor[0] >= self.columns:
                log.debug("edge is out of view")
                strlen = realwidth(self.value[self.pos[1] + self.cursor[1]])
                self.pos[0] = max(0, strlen - self.columns + 1)
                self.cursor[0] = self.columns - 1

                if not shift:
                    out.append(move(cursor_shift))

                shift = True

            elif diff > 0:
                out.append(self.term.move_left(diff))

            elif diff < 0:
                out.append(self.term.move_right(-diff))

        out.append(self.redraw() if shift else move(cursor_shift))
        log.debug(
            f"{'up' if distance < 0 else 'down'} {self.pos} {self.cursor}"
        )

        return "".join(out)

    def _kp_left(self) -> str:
        return self._horizontal(-1)

    def _kp_right(self) -> str:
        return self._horizontal(1)

    def _kp_home(self) -> str:
        return self._horizontal(-(self.pos[0] + self.cursor[0]))

    def _kp_end(self) -> str:
        return self._horizontal(-self.edge_diff)

    def _kp_up(self) -> str:
        return self._vertical(-1)

    def _kp_down(self) -> str:
        return self._vertical(1)

    def _kp_pgup(self) -> str:
        return self._vertical(-(self.rows - 1))

    def _kp_pgdown(self) -> str:
        return self._vertical(self.rows - 1)

    def process_keystroke(self, ks: Keystroke) -> str:
        """
        Process keystroke and produce output (if any).

        Args:
            ks: The keystroke to process.

        Returns:
            The output sequence for screen updates.
        """

        handlers = {
            self.term.KEY_BACKSPACE: self._kp_backspace,
            self.term.KEY_DELETE: self._kp_delete,
            self.term.KEY_LEFT: self._kp_left,
            self.term.KEY_RIGHT: self._kp_right,
            self.term.KEY_HOME: self._kp_home,
            self.term.KEY_END: self._kp_end,
        }

        if self.rows > 1:
            handlers = {
                **handlers,
                **{
                    self.term.KEY_UP: self._kp_up,
                    self.term.KEY_DOWN: self._kp_down,
                    self.term.KEY_PGUP: self._kp_pgup,
                    self.term.KEY_PGDOWN: self._kp_pgdown,
                },
            }

        # TODO general: tab
        # TODO multiline: under/overflow, enter

        if ks.code in handlers:
            return handlers[ks.code]()

        if ks.is_sequence:
            log.debug(f"swallowing sequence {ks!r}")
            return ""

        if self.limit[0] > 0 and self.pos[0] + self.cursor[0] >= self.limit[0]:
            log.debug(f"reached text limit, discarding {ks!r}")
            return ""

        ucs = str(ks)

        if not self.term.length(ucs):
            ordinal = ord(ucs)

            # control characters; do not add to editor value
            if 0 <= ordinal <= 31:
                log.debug(f"discarding: {hex(ordinal)}")
                return ""

        # handle typed character or pasted grapheme

        # TODO fix bug when inserting behind graphemes

        dist = realwidth(ucs)
        ucslen = len(ucs)
        row, before, after = self._row_vars
        log.debug((row, before, after))
        self.value[self.pos[1] + self.cursor[1]] = before + ucs + after
        self.cursor[0] += dist
        log.debug(
            f"{self.pos} {self.cursor} {self._cursor_offset} {self.value!r}"
        )

        if not self.at_end and self.cursor[0] >= self.columns:
            self.cursor[0] -= dist
            self.pos[0] += ucslen
            log.debug("shifting visible area to right")

            return self.redraw()

        after = after[: -ucslen - 1]
        afterlen = realwidth(after)
        move_left = (
            afterlen
            if (
                self.pos[0] + self.cursor[0] + self._cursor_offset
                < realwidth(self.value[self.pos[1] + self.cursor[1]])
            )
            else afterlen
        )

        out = [ucs, after]

        if move_left > 0:
            out.append(self.term.move_left(move_left))

        return self.color("".join(out))
