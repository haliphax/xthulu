"editors module"

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

    def __init__(self, term, rows, columns, **kwargs):
        #: Terminal to use for sequences
        self.term = term
        #: Height in rows
        self.rows = rows
        #: Width in columns
        self.columns = columns

        if 'value' not in kwargs:
            for i in range(rows):
                self.value.append('')

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
    def color(self):
        """
        Color property; setting it also sets the internal Terminal callable

        :rtype: callable
        """

        return getattr(self.term, self._color_str)

    @color.setter
    def color(self, val):
        self._color_str = val
        self._color = getattr(self.term, val)

    def redraw(self, redraw_cursor=True, anchor=False):
        """
        Output sequence to redraw editor

        :param bool redraw_cursor: Redraw cursor position as well
        :param bool anchor: Reset anchor position as well
        :rtype: str
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

    def redraw_cursor(self):
        """
        Output sequence to restore cursor position; assumes cursor is already
        located at top-left of editor if self.corner is unset

        :rtype: str
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

    def reset_anchor(self):
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

    def process_keystroke(self, ks):
        """
        Process keystroke and produce output (if any)

        :param :class:`blessed.keyboard.Keystroke` ks: Keystroke object
            (e.g. from `inkey`)
        :returns: Updated output for the editor display
        :rtype: str
        """

        row = self.value[self.pos[1] + self.cursor[1]]
        before = row[:self.pos[0] + self.cursor[0]]
        after = row[self.pos[0] + self.cursor[0]:]

        # TODO split handlers into own functions (self.home, self.end, etc.)
        # TODO general: tab
        # TODO multiline: up/down, under/overflow, enter

        if ks.code == self.term.KEY_BACKSPACE:
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

        elif ks.code == self.term.KEY_DELETE:
            if self.pos[0] >= len(self.value[self.pos[1]]):
                log.debug('at end of line, nothing to delete')
                return ''

            after = after[1:]
            self.value[self.pos[1]] = before + after
            after = after[:min(len(after), self.columns - self.cursor[0])]
            log.debug(f'delete "{self.value[self.pos[1]]}"')

            return self._color(after + ' ' +
                               self.term.move_x(self.cursor[0] + 1))

        elif ks.code == self.term.KEY_LEFT:
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

        elif ks.code == self.term.KEY_RIGHT:
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

        elif ks.code == self.term.KEY_HOME:
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

        elif ks.code == self.term.KEY_END:
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
            self.cursor[0] = min(strlen, self.columns - 1)
            log.debug(f'end {self.pos}')

            return self.redraw(anchor=True) if shift \
                else self.term.move_right(self.cursor[0] - prev)

        elif ks.is_sequence:
            log.debug(f'swallowing sequence {ks!r}')
            return ''

        elif self.limit[0] > 0 and self.pos[0] >= self.limit[0]:
            log.debug(f'reached text limit, discarding {ks!r}')
            return ''

        ucs = str(ks)

        if not self.term.length(ucs):
            log.debug('zero length ucs')
            return ''

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
    def rows(self):
        """
        A line editor only has a single row

        :rtype: int
        """

        return 1

    @rows.setter
    def rows(self, val):
        pass
