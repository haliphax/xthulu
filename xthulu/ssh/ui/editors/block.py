"""Block editor"""

# type checking
from typing import Callable

# 3rd party
from blessed.keyboard import Keystroke

# local
from ....logger import log
from ...console.grapheme import Grapheme
from ...console.grapheme_buffer import GraphemeBuffer
from ...terminal.proxy_terminal import ProxyTerminal

# TODO draw_line() with check for first char being None


class BlockEditor:

    """Block editor (multiple lines)"""

    value: list[GraphemeBuffer] = []
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
            self.value = [GraphemeBuffer() for _ in range(rows)]

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

            strlen = len(self.value[self.pos[1]])
            self.pos[0] = max(0, strlen - self.columns)

        if "cursor" not in kwargs:
            if strlen == 0:
                strlen = len(self.value[self.pos[1]])

            self.cursor[0] = min(self.columns - 1, max(0, strlen))
            self.cursor[1] = min(self.rows - 1, max(0, len(self.value) - 1))

        log.debug(f"corner: {self.corner}")
        log.debug(f"pos: {self.pos}")
        log.debug(f"cursor: {self.cursor}")

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
    def current_row(self):
        """The current row's value."""

        return (
            self.value[self.abs_cursor[1]] if self.value else GraphemeBuffer()
        )

    @property
    def abs_cursor(self):
        """The cursor's absolute position within the entire editor value."""

        return (self.pos[0] + self.cursor[0], self.pos[1] + self.cursor[1])

    @property
    def cursor_boundary(self):
        """The relative bottom-right corner of the editor panel."""

        return (self.pos[0] + self.columns, self.pos[1] + self.rows)

    @property
    def at_end(self) -> bool:
        """Whether the cursor is at the end of the editor."""

        if self.limit[0] == 0:
            return False

        return (
            self.cursor[0] >= self.columns - 1
            and len(self.current_row) >= self.limit[0]
        )

    @property
    def edge_diff(self) -> int:
        """How far the cursor is from the edge of the current row."""

        return self.pos[0] + self.cursor[0] - len(self.current_row) - 1

    def _row_vars(self, index: int | None = None, split: int | None = None):
        abs_cursor = self.abs_cursor
        row = self.value[index] if index else self.current_row

        if split is None:
            split = abs_cursor[0]

        before = GraphemeBuffer(row[:split])
        after = GraphemeBuffer(row[split:])

        return row, before, after

    def redraw(self, cursor=True, anchor=True) -> str:
        """
        Output sequence to redraw editor.

        Args:
            cursor: Whether to redraw cursor position after output.
            anchor: Whether to reset anchor position before output.

        Returns:
            The output string to redraw the editor/cursor.
        """

        out: list[str] = []
        travel = 0

        if anchor:
            out.append(self.reset_anchor())

        for i in range(self.rows):
            if i > 0:
                out.append("\n")
                travel += 1

            if self.corner[0] is not None:
                out.append(self.term.move_x(self.corner[0]))
            else:
                out.append(self.term.move_left(self.columns))

            index = self.pos[1] + i
            out.append(self.redraw_line(index))

        if cursor and travel > 0:
            out.append(self.term.move_up(travel))

        log.debug("redrawing editor")

        return "".join(out)

    def redraw_cursor(self) -> str:
        """
        Output sequence to restore cursor position; assumes cursor is already
        located at top-left of editor if self.corner is unset.

        Returns:
            The output sequence to redraw the cursor.
        """

        out: list[str] = []

        # move cursor back to top left before adjusting to self.cursor offset
        if self.corner[0] is not None:
            out.append(self.term.move_x(self.corner[0]))

        if self.corner[1] is not None:
            out.append(self.term.move_y(self.corner[1]))

        # adjust offset
        if self.cursor[0] > 0:
            out.append(self.term.move_right(self.cursor[0]))

        if self.cursor[1] > 0:
            out.append(self.term.move_down(self.cursor[1]))

        log.debug("redrawing cursor")

        return "".join(out)

    def reset_anchor(self) -> str:
        """
        Assuming the cursor has not moved since the editor was responsible for
        it, this will reset the on-screen cursor to the top-left corner of the
        editor.

        Returns:
            The output sequence to reset the anchor.
        """

        out: list[str] = []

        if self.cursor[0] > 0:
            out.append(self.term.move_left(self.cursor[0]))

        if self.cursor[1] > 0:
            out.append(self.term.move_up(self.cursor[1]))

        log.debug("resetting anchor")

        return "".join(out)

    def reset(self):
        """Reset the editor's value, cursor, and offset position."""

        self.cursor = [0, 0]
        self.pos = [0, 0]
        self.value = [GraphemeBuffer() for _ in range(self.rows)]

    def redraw_current_line(self, cursor=True, left=True, right=True) -> str:
        abs_cursor = self.abs_cursor

        return self.redraw_line(
            abs_cursor[1], cursor=cursor, left=left, right=right
        )

    def redraw_line(
        self, index: int, cursor=True, left=True, right=True
    ) -> str:
        """
        Output sequence to redraw the given line, accounting for half-width
        graphemes that would hang off the edge of the panel.

        Args:
            cursor: Whether to reset the cursor after output.
            left: Whether to include the half of the line before the cursor.
            right: Whether to include the half of the line after the cursor.

        Returns:
            String of sequences for redrawing the current line.
        """

        if not (left or right):
            return ""

        _, before, after = self._row_vars(index)
        beforelen = len(before)
        afterlen = len(after)
        left_width = min(self.cursor[0], beforelen)
        right_width = min(self.columns - self.cursor[0], afterlen)
        left_half = GraphemeBuffer(before[-left_width:]) if left else None
        right_half = GraphemeBuffer(after[:right_width]) if right else None
        travel = 0
        out: list[str] = []

        if left_half:
            if cursor and self.cursor[0] > 0:
                out.append(self.term.move_left(self.cursor[0]))

            first = left_half[0] if left_half else Grapheme()

            # handle full-width graphemes hanging off the left edge
            if left and first is None:
                log.debug("hanging grapheme, left edge")
                left_half.pop(0)
                left_half = (
                    GraphemeBuffer.from_str(
                        "\u2026" if self.term.encoding == "utf-8" else "<"
                    )
                    + left_half
                )

            out.append(str(left_half))

        if right_half:
            # overflowing right edge
            if afterlen > self.columns - self.cursor[0]:
                last = right_half[-1]

                if last and last.width > 1:
                    log.debug("hanging grapheme, right edge")
                    right_half.pop()
                    right_half += (
                        "\u2026" if self.term.encoding == "utf-8" else ">"
                    )

            assert right_half is not None
            right_width = len(right_half)

            travel += right_width
            out.append(str(right_half))

        log.debug(f"left {left_width} right {right_width}")
        remaining_space = self.columns - left_width - right_width
        log.debug(f"remaining space: {remaining_space}")

        if remaining_space > 0:
            # handle trailing "ghost" glyphs by overwriting with empty space
            travel += remaining_space
            out += " " * remaining_space

        if cursor and travel > 0:
            out.append(self.term.move_left(travel))

        return self.color("".join(out))

    def _kp_backspace(self) -> str:
        row, before, after = self._row_vars()
        log.debug((row, before, after))

        if self.pos[0] <= 0 and self.cursor[0] == 0:
            log.debug("at start of line, nothing to backspace")
            return ""

        abs_cursor = self.abs_cursor
        deleted = None

        while deleted is None:
            deleted = before.pop()

        result = GraphemeBuffer(before + after)
        self.value[abs_cursor[1]] = result
        self.cursor[0] -= deleted.width
        log.debug(f"backspace {self.pos} {self.cursor} {self.current_row!r}")

        if self.cursor[0] < 0:
            self.pos[0] = max(0, self.pos[0] - 1)
            self.cursor[0] = 0

            return self.redraw()

        return "".join(
            (
                self.term.move_left(deleted.width),
                self.redraw_current_line(left=False),
            )
        )

    def _kp_delete(self) -> str:
        row, before, after = self._row_vars()

        if self.pos[0] >= len(row):
            log.debug("at end of line, nothing to delete")
            return ""

        abs_cursor = self.abs_cursor
        delete = after[0]
        assert delete is not None
        after.pop(0)
        self.value[abs_cursor[1]] = before + after
        log.debug(f"delete {self.pos} {self.cursor} {self.current_row!r}")

        return self.redraw_current_line(left=False)

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

        row, before, after = self._row_vars()
        log.debug((row, before, after))
        abs_cursor = self.abs_cursor
        strlen = len(row)
        blen = len(before)
        log.debug(f"before: {blen}")

        if distance == 1 and after:
            first = after[0]
            log.debug(f"first: {first!r}")
            distance = first.width if first else 1

        elif distance == -1 and blen > 1:
            idx = 0
            last = None

            while last is None:
                idx -= 1
                last = before[idx]

            distance = -last.width

        log.debug(f"distance: {distance}")

        if distance < 0 and abs_cursor[0] <= 0:
            log.debug("already at start of line")

            return ""

        if distance > 0 and abs_cursor[0] > strlen:
            log.debug("already at end of line")

            return ""

        shift = False
        move: Callable[..., str]
        new_abs = abs_cursor[0] + distance
        target = None

        if new_abs < strlen:
            target = row[abs_cursor[0] + distance]
            log.debug(f"target: {target!r}")

            # don't land on half of a grapheme
            while target is None:
                distance += 1 if distance > 0 else -1
                target = row[abs_cursor[0] + distance]

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
                    strlen - self.columns + 1, self.pos[0] + abs_distance + 1
                )
                new_cursor = self.columns - 1
                shift = True

            move = self.term.move_right

        out: list[str] = []
        self.cursor[0] = new_cursor

        if shift:
            out.append(self.redraw())
        else:
            out.append(move(abs(distance)))

        log.debug(
            f"{'left' if distance < 0 else 'right'} {self.pos} {self.cursor} "
            f"{target!r} {distance}"
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

        abs_cursor = self.abs_cursor

        if distance < 0 and abs_cursor[1] == 0:
            log.debug("already at start of editor")

            return ""

        if distance > 0 and abs_cursor[1] == len(self.value) - 1:
            log.debug("already at end of editor")

            return ""

        snap_to_edge = self.edge_diff >= 0
        shift = False
        strlen = len(self.value)
        clamp_low = -(self.pos[1] + self.cursor[1])
        clamp_high = strlen - self.pos[1] - self.cursor[1]
        log.debug(f"distance clamp: {clamp_low} - {clamp_high}")
        distance = min(clamp_high, max(clamp_low, distance))
        new_cursor = self.cursor[1] + distance
        log.debug(f"new cursor: {new_cursor}")
        out: list[str] = []

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
                min(self.pos[1] + distance, strlen - self.rows),
            )

        log.debug(f"clamped new cursor: {new_cursor}")
        cursor_shift = abs(self.cursor[1] - new_cursor)
        log.debug(f"cursor shift: {cursor_shift}")

        if shift and cursor_shift > 0:
            out.append(move(cursor_shift))

        self.cursor[1] = new_cursor
        strlen = len(self.current_row)
        diff = self.edge_diff

        if not snap_to_edge and diff > 0:
            log.debug("past end of line")
            snap_to_edge = True

        if snap_to_edge:
            log.debug("snapping to edge")
            self.cursor[0] -= diff

            if self.cursor[0] < 0 or self.cursor[0] >= self.columns:
                log.debug("edge is out of view")
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
        row = self.current_row
        strlen = len(row)
        abs_cursor = self.abs_cursor
        target: Grapheme | None = None

        try:
            cur_char = self.current_row[abs_cursor[0]]

            if len(row) and (abs_cursor[0] > strlen or not cur_char):
                offset = abs_cursor[0] - strlen - 1 if cur_char else 1
                log.debug(
                    f"finding valid position: {strlen} {abs_cursor[0]} {offset}"
                )
                target = row[abs_cursor[0] - offset]

                while target is None:
                    offset += 1
                    target = row[abs_cursor[0] - offset]

                if offset > 0:
                    self.cursor[0] -= offset
                    out.append(self.term.move_left(offset))
        except IndexError:
            pass

        log.debug(
            f"{'up' if distance < 0 else 'down'} {self.pos} {self.cursor} "
            f"{target!r}"
        )

        return "".join(out)

    def _kp_left(self) -> str:
        return self._horizontal(-1)

    def _kp_right(self) -> str:
        return self._horizontal(1)

    def _kp_home(self) -> str:
        return self._horizontal(-(self.pos[0] + self.cursor[0]))

    def _kp_end(self) -> str:
        log.debug(self.edge_diff)
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

        dist = len(ucs)
        ucslen = len(ucs)
        row, before, after = self._row_vars()
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

        abs_cursor = self.abs_cursor
        after = GraphemeBuffer(after[: -ucslen - 1])
        last = after[-1] if after else None

        if (
            last
            and last.width > 1
            and abs_cursor[0] + self.columns >= len(self.current_row)
        ):
            after = after[:-1]

        move_left = len(after)
        out = [ucs, str(after)]

        if move_left > 0:
            out.append(self.term.move_left(move_left))

        return self.color("".join(out))
