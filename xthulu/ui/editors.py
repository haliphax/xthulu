"""editors module"""

# stdlib
from typing import Callable

# 3rd party
from blessed.keyboard import Keystroke

# local
from .. import log
from ..terminal.proxy_terminal import ProxyTerminal


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
    _color_str = "bold_white_on_blue"
    _color = None

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
        textlen = 0

        if "pos" not in kwargs:
            for i in range(max(0, len(self.value) - self.rows)):
                if len(self.value[i]) > 0:
                    self.pos[1] = i

            textlen = len(self.value[self.pos[1]])
            self.pos[0] = max(0, textlen - self.columns)

        if "cursor" not in kwargs:
            if textlen == 0:
                textlen = len(self.value[self.pos[1]])

            self.cursor[0] = min(self.columns - 1, max(0, textlen))
            self.cursor[1] = min(self.rows - 1, max(0, len(self.value) - 1))

        log.debug(f"corner = {self.corner}")
        log.debug(f"pos = {self.pos}")
        log.debug(f"cursor = {self.cursor}")

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
            and len(self.value[self.pos[1]]) >= self.limit[0]
        )

    def redraw(self, redraw_cursor=True, anchor=False) -> str:
        """
        Output sequence to redraw editor.

        Args:
            redraw_cursor: Redraw cursor position as well.
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
            out += self.color(" " * (self.columns - len(text)))
            out += self.term.move_left(self.columns)

        log.debug("redrawing editor")

        if redraw_cursor:
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
        before = row[: self.pos[0] + self.cursor[0]]
        after = row[self.pos[0] + self.cursor[0] :]

        return row, before, after

    def kp_backspace(self) -> str:
        """
        Handle KEY_BACKSPACE.

        Returns:
            The output sequence for screen updates.
        """

        _, before, after = self._row_vars

        if self.pos[0] <= 0 and self.cursor[0] == 0:
            log.debug("at start of line, nothing to backspace")
            return ""

        if self.cursor[0] <= 0:
            self.pos[0] = max(0, self.pos[0] - 1)

        self.value[self.pos[1] + self.cursor[1]] = before[:-1] + after
        out = ""

        after = after[: min(len(after), self.columns - self.cursor[0])]

        if self.cursor[0] > 0:
            after += " "
            out += self.term.move_left()
            self.cursor[0] -= 1

        out += self.color(after + self.term.move_left(len(after)))
        log.debug(
            f"backspace {self.pos} {self.cursor} "
            f"{self.value[self.pos[1] + self.cursor[1]]!r}"
        )

        return out

    def kp_delete(self) -> str:
        """
        Handle KEY_DELETE.

        Returns:
            The output sequence for screen updates.
        """

        _, before, after = self._row_vars

        if self.pos[0] >= len(self.value[self.pos[1]]):
            log.debug("at end of line, nothing to delete")
            return ""

        after = after[1:]
        self.value[self.pos[1] + self.cursor[1]] = before + after
        after = after[: min(len(after), self.columns - self.cursor[0])]

        if self.cursor[0] + len(after) <= self.columns - 1:
            after += " "

        log.debug(f'delete "{self.value[self.pos[1] + self.cursor[1]]}"')

        return self.color(after + self.term.move_left(len(after)))

    def kp_left(self) -> str:
        """
        Handle KEY_LEFT.

        Returns:
            The output sequence for screen updates.
        """

        if self.cursor[0] <= 0 and self.pos[0] <= 0:
            log.debug("already at start of line")
            return ""

        shift = False

        if self.cursor[0] <= 0:
            shift = True
            self.pos[0] -= 1
            log.debug("shifting visible area left")

        self.cursor[0] = max(0, self.cursor[0] - 1)
        log.debug(f"left {self.pos} {self.cursor}")

        return self.redraw(anchor=True) if shift else self.term.move_left()

    def kp_right(self) -> str:
        """
        Handle KEY_RIGHT.

        Returns:
            The output sequence for screen updates.
        """

        if self.pos[0] + self.cursor[0] >= len(
            self.value[self.pos[1] + self.cursor[1]]
        ):
            log.debug("already at end of line")
            return ""

        shift = False

        if self.cursor[0] >= self.columns - 1:
            shift = True
            self.pos[0] += 1
            log.debug("shifting visible area right")

        self.cursor[0] = min(self.columns - 1, self.cursor[0] + 1)
        log.debug(f"right {self.pos} {self.cursor}")

        return self.redraw(anchor=True) if shift else self.term.move_right()

    def kp_home(self) -> str:
        """
        Handle KEY_HOME.

        Returns:
            The output sequence for screen updates.
        """

        if self.cursor[0] == 0:
            log.debug("already at start of line")
            return ""

        shift = False

        if self.pos[0] > 0:
            shift = True
            log.debug("shifting visible area left")

        lastpos = self.pos.copy()
        lastcurs = self.cursor.copy()
        out = self.term.move_left(self.cursor[0])
        self.pos[0] = 0
        self.cursor[0] = 0
        out += self.redraw() if shift else ""
        log.debug(f"home {lastpos} {lastcurs} => {self.pos} {self.cursor}")

        return out

    def kp_end(self) -> str:
        """
        Handle KEY_END.

        Returns:
            The output sequence for screen updates.
        """

        strlen = len(self.value[self.pos[1] + self.cursor[1]])

        if self.pos[0] + self.cursor[0] >= strlen:
            log.debug("already at end of line")
            return ""

        shift = False

        if strlen - self.pos[0] > self.columns:
            shift = True
            self.pos[0] = max(0, strlen - self.columns + 1)
            log.debug("shifting visible area right")

        prev = self.cursor[0]
        self.cursor[0] = min(strlen - self.pos[0], self.columns - 1)
        log.debug(f"end {self.pos}")

        return (
            self.redraw(anchor=True)
            if shift
            else self.term.move_right(self.cursor[0] - prev)
        )

    def kp_up(self) -> str:
        """
        Handle KEY_UP.

        Returns:
            The output sequence for screen updates.
        """

        if self.cursor[1] <= 0 and self.pos[1] <= 0:
            log.debug("already at start of editor")
            return ""

        shift = False
        old_cursor = self.cursor[0]

        if self.cursor[1] <= 0:
            shift = True
            self.pos[1] -= 1
            log.debug("shifting visible area up")

        self.cursor[1] = max(0, self.cursor[1] - 1)
        out = ""
        textlen = len(self.value[self.pos[1] + self.cursor[1]])

        if self.pos[0] + self.cursor[0] > textlen:
            self.cursor[0] = textlen
            out += self.term.move_left(old_cursor - self.cursor[0])

        log.debug(f"up {self.pos} {self.cursor}")
        out += self.redraw(anchor=True) if shift else self.term.move_up()

        return out

    def kp_down(self) -> str:
        """
        Handle KEY_DOWN.

        Returns:
            The output sequence for screen updates.
        """

        if self.pos[1] + self.cursor[1] >= len(self.value) - 1:
            log.debug("already at end of editor")
            return ""

        shift = False
        old_cursor = self.cursor[0]

        if self.cursor[1] >= self.rows - 1:
            shift = True
            self.pos[1] += 1
            log.debug("shifting visible area down")

        self.cursor[1] = min(self.rows - 1, self.cursor[1] + 1)
        out = ""
        textlen = len(self.value[self.pos[1] + self.cursor[1]])

        if self.pos[0] + self.cursor[0] > textlen:
            self.cursor[0] = textlen
            out += self.term.move_left(old_cursor - self.cursor[0])

        log.debug(f"down {self.pos} {self.cursor}")
        out += self.redraw(anchor=True) if shift else self.term.move_down()

        return out

    def process_keystroke(self, ks: Keystroke) -> str:
        """
        Process keystroke and produce output (if any).

        Args:
            ks: The keystroke to process.

        Returns:
            The output sequence for screen updates.
        """

        handlers = {
            self.term.KEY_BACKSPACE: self.kp_backspace,
            self.term.KEY_DELETE: self.kp_delete,
            self.term.KEY_LEFT: self.kp_left,
            self.term.KEY_RIGHT: self.kp_right,
            self.term.KEY_HOME: self.kp_home,
            self.term.KEY_END: self.kp_end,
        }

        if self.rows > 1:
            handlers = {
                **handlers,
                **{
                    self.term.KEY_UP: self.kp_up,
                    self.term.KEY_DOWN: self.kp_down,
                },
            }

        # TODO general: tab
        # TODO multiline: up/down, under/overflow, enter

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
            log.debug("zero length ucs")
            return ""

        # handle typed character

        _, before, after = self._row_vars
        self.value[self.pos[1] + self.cursor[1]] = before + ucs + after
        self.cursor[0] += 1
        log.debug(f"{self.pos} {self.cursor} {self.value}")

        if not self.at_end and self.cursor[0] >= self.columns:
            self.cursor[0] -= 1
            self.pos[0] += 1
            log.debug("shifting visible area to right")

            return self.redraw(anchor=True)

        after = after[: min(len(after), self.columns - self.cursor[0])]
        move_left = (
            len(after)
            if (
                self.pos[0] + self.cursor[0]
                < len(self.value[self.pos[1] + self.cursor[1]])
            )
            else len(after) - 1
        )

        out = [ucs, after]

        if move_left > 0:
            out.append(self.term.move_left(move_left))

        return self.color("".join(out))


class LineEditor(BlockEditor):
    """Line editor (single line)"""

    def __init__(self, term, columns, limit=0, *args, **kwargs):
        super().__init__(term, 1, columns, limit=(limit, 1), *args, **kwargs)

    @property
    def rows(self) -> int:
        """A line editor only has a single row."""

        return 1

    @rows.setter
    def rows(self, val: int):
        if val != 1:
            raise ValueError("LineEditor must have exactly 1 row")
