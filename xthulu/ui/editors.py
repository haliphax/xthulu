"editors module"

# stdlib
from typing import Callable
# 3rd party
from blessed import Terminal
# local
from .. import log


class BlockEditor(object):

    "Block editor (multiple lines)"

    #: Editor text
    value = []
    #: Text length limit (width, height)
    limit = [0, 0]
    #: Top-left corner of editor on screen (x, y)
    corner = [None, None]
    #: Cursor offset from top-left corner on screen (x, y)
    cursor = [0, 0]
    #: Position within corpus of corner of editor (x, y)
    pos = [0, 0]

    # internals
    _color_str = 'bold_white_on_blue'
    _color = None

    def __init__(self, term: Terminal, rows: int, columns: int, **kwargs):
        #: Terminal to use for sequences
        self.term = term
        #: Height in rows
        self.rows = rows
        #: Width in columns
        self.columns = columns

        if 'value' not in kwargs:
            self.value = ['',] * rows

        if 'color' in kwargs:
            self._color_str = kwargs['color']
            del kwargs['color']

        for k in kwargs:
            setattr(self, k, kwargs[k])

        self._color = getattr(term, self._color_str)

        if 'pos' not in kwargs:
            for i in range(len(self.value)):
                if len(self.value[i]) > 0:
                    self.pos[1] = i

            textlen = len(self.value[self.pos[1]])
            self.pos[0] = max(0, textlen - self.columns)

        if 'cursor' not in kwargs:
            self.cursor[0] = min(self.columns - 1, max(0, textlen))
            self.cursor[1] = min(self.rows - 1, max(0, len(self.value) - 1))

        log.debug(f'corner = {self.corner}')
        log.debug(f'pos = {self.pos}')
        log.debug(f'cursor = {self.cursor}')

    @property
    def color(self) -> Callable:
        """
        Color property; setting it also sets the internal Terminal callable
        """

        return getattr(self.term, self._color_str)

    @color.setter
    def color(self, val):
        self._color_str = val
        self._color = getattr(self.term, val)

    def redraw(self, redraw_cursor=True, anchor=False) -> str:
        """
        Output sequence to redraw editor

        :param redraw_cursor: Redraw cursor position as well
        :param anchor: Reset anchor position as well
        """

        out = ''
        left = self.pos[0]
        top = self.pos[1]
        spread = self.rows - top
        lastlen = 0
        travel = 0

        if anchor:
            out += self.reset_anchor()

        for i in range(spread):
            if i > 0:
                out += '\r\n'
                travel += 1

            if self.corner[0] is not None:
                out += self.term.move_x(self.corner[0])

            out += self._color(' ' * self.columns)
            out += self.term.move_left(self.columns)
            text = self.value[top + i][left:left + self.columns]
            out += self._color(text)
            lastlen = len(text)

        log.debug('redrawing editor')

        if redraw_cursor:
            if lastlen > 0:
                out += self.term.move_left(lastlen)

            if travel > 0:
                out += self.term.move_up(travel)

            out += self.redraw_cursor()

        return out

    def redraw_cursor(self) -> str:
        """
        Output sequence to restore cursor position; assumes cursor is already
        located at top-left of editor if self.corner is unset
        """

        out = ''

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

        log.debug('redrawing cursor')

        return out

    def reset_anchor(self) -> str:
        """
        Assuming the cursor has not moved since the editor was responsible for
        it, this will reset the on-screen cursor to the top-left corner of the
        editor.
        """

        out = ''

        if self.cursor[0] > 0:
            out += self.term.move_left(self.cursor[0])

        if self.cursor[1] > 0:
            out += self.ter.move_up(self.cursor[1])

        log.debug('resetting anchor')

        return out

    @property
    def _row_vars(self):
        row = self.value[self.pos[1] + self.cursor[1]]
        before = row[:self.pos[0] + self.cursor[0]]
        after = row[self.pos[0] + self.cursor[0]:]

        return row, before, after

    def kp_backspace(self) -> str:
        "Handle KEY_BACKSPACE."

        _, before, after = self._row_vars

        if self.pos[0] <= 0 and self.cursor[0] == 0:
            log.debug('at start of line, nothing to backspace')
            return ''

        if self.cursor[0] <= 0:
            self.pos[0] = max(0, self.pos[0] - 1)

        self.value[self.pos[1]] = before[:-1] + after
        out = ''

        after = after[:min(len(after), self.columns - self.cursor[0])]

        if self.cursor[0] > 0:
            after += ' '
            out += self.term.move_left
            self.cursor[0] -= 1

        out += self._color(after + self.term.move_left(len(after)))
        log.debug(f'backspace {self.pos} {self.cursor} '
                    f'{self.value[self.pos[1]]!r}')

        return out

    def kp_delete(self) -> str:
        "Handle KEY_DELETE."

        _, before, after = self._row_vars

        if self.pos[0] >= len(self.value[self.pos[1]]):
            log.debug('at end of line, nothing to delete')
            return ''

        after = after[1:]
        self.value[self.pos[1]] = before + after
        after = after[:min(len(after), self.columns - self.cursor[0])]

        if self.cursor[0] + len(after) <= self.columns - 1:
            after += ' '

        log.debug(f'delete "{self.value[self.pos[1]]}"')

        return self._color(after + self.term.move_left(len(after)))

    def kp_left(self) -> str:
        "Handle KEY_LEFT."

        if self.cursor[0] <= 0 and self.pos[0] <= 0:
            log.debug('already at start of line')
            return ''

        shift = False

        if self.cursor[0] <= 0:
            shift = True
            self.pos[0] -= 1
            log.debug('shifting visible area left')

        self.cursor[0] = max(0, self.cursor[0] - 1)
        log.debug(f'left {self.pos} {self.cursor}')

        return self.redraw(anchor=True) if shift else self.term.move_left

    def kp_right(self) -> str:
        "Handle KEY_RIGHT."

        if self.pos[0] + self.cursor[0] >= len(self.value[self.pos[1]]):
            log.debug('already at end of line')
            return ''

        shift = False

        if self.cursor[0] >= self.columns - 1:
            shift = True
            self.pos[0] += 1
            log.debug('shifting visible area right')

        self.cursor[0] = min(self.columns - 1, self.cursor[0] + 1)
        log.debug(f'right {self.pos} {self.cursor}')

        return self.redraw(anchor=True) if shift else self.term.move_right

    def kp_home(self) -> str:
        "Handle KEY_HOME."

        if self.cursor[0] == 0:
            log.debug('already at start of line')
            return ''

        shift = False

        if self.pos[0] > 0:
            shift = True
            log.debug('shifting visible area left')

        lastpos = self.pos.copy()
        lastcurs = self.cursor.copy()
        out = self.term.move_left(self.cursor[0])
        self.pos[0] = 0
        self.cursor[0] = 0
        out += self.redraw() if shift else ''
        log.debug(f'home {lastpos} {lastcurs} => {self.pos} {self.cursor}')

        return out

    def kp_end(self) -> str:
        "Handle KEY_END."

        strlen = len(self.value[self.pos[1]])

        if self.pos[0] + self.cursor[0] >= strlen:
            log.debug('already at end of line')
            return ''

        shift = False

        if strlen - self.pos[0] > self.columns:
            shift = True
            self.pos[0] = max(0, strlen - self.columns + 1)
            log.debug('shifting visible area right')

        prev = self.cursor[0]
        self.cursor[0] = min(strlen - self.pos[0], self.columns - 1)
        log.debug(f'end {self.pos}')

        return self.redraw(anchor=True) if shift \
            else self.term.move_right(self.cursor[0] - prev)

    def process_keystroke(self, ks) -> str:
        """
        Process keystroke and produce output (if any)

        :param :class:`blessed.keyboard.Keystroke` ks: Keystroke object
            (e.g. from `inkey`)
        :returns: Updated output for the editor display
        :rtype: str
        """

        handlers = {
            self.term.KEY_BACKSPACE: self.kp_backspace,
            self.term.KEY_DELETE: self.kp_delete,
            self.term.KEY_LEFT: self.kp_left,
            self.term.KEY_RIGHT: self.kp_right,
            self.term.KEY_HOME: self.kp_home,
            self.term.KEY_END: self.kp_end,
        }

        # TODO general: tab
        # TODO multiline: up/down, under/overflow, enter

        if ks.code in handlers:
            return handlers[ks.code]()

        if ks.is_sequence:
            log.debug(f'swallowing sequence {ks!r}')
            return ''

        if self.limit[0] > 0 and self.pos[0] >= self.limit[0]:
            log.debug(f'reached text limit, discarding {ks!r}')
            return ''

        ucs = str(ks)

        if not self.term.length(ucs):
            log.debug('zero length ucs')
            return ''

        # handle typed character

        _, before, after = self._row_vars
        self.value[self.pos[1]] = before + ucs + after
        self.cursor[0] += 1
        log.debug(f"{self.pos} {self.value}")

        if self.cursor[0] >= self.columns:
            self.cursor[0] -= 1
            self.pos[0] += 1
            log.debug('shifting visible area to right')

            return self.redraw(anchor=True)

        after = after[:min(len(after), self.columns - self.cursor[0])]
        move_left = len(after) \
            if self.pos[0] + self.cursor[0] < len(self.value[self.pos[1]]) \
            else len(after) - 1

        return self._color(ucs + after + self.term.move_left(move_left))


class LineEditor(BlockEditor):

    "Line editor (single line)"

    def __init__(self, term, columns, *args, **kwargs):
        super().__init__(term, 1, columns, *args, **kwargs)

    @property
    def rows(self) -> int:
        "A line editor only has a single row"

        return 1

    @rows.setter
    def rows(self, val: int):
        pass
