"editors module"

# local
from .. import log


class BlockEditor(object):

    "Block editor (multiple lines)"

    #: Editor text
    value = []
    #: Text length limit
    limit = [0, 0]
    #: Top-left corner of editor
    corner = [None, None]
    #: Cursor position within corpus (not screen position)
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

        for k in kwargs:
            setattr(self, k, kwargs[k])

        self._color = getattr(term, self._color_str)

        for i in range(len(self.value)):
            if len(self.value[i]) == 0:
                self.pos[0] = i

        self.pos[1] = len(self.value[self.pos[0]])

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

    def redraw(self, redraw_cursor=True):
        """
        Output sequence to redraw editor

        :param bool redraw_cursor: Redraw cursor position as well
        :rtype: str
        """

        out = ''
        lenval = len(self.value)
        longest = 0

        if (self.corner[0] is not None):
            out += self.term.move_y(self.corner[0])

        for i in range(self.rows):
            if i > 0:
                out += '\r\n'

            if (self.corner[1] is not None):
                out += self.term.move_x(self.corner[1])

            out += self._color(' ' * self.columns)

            if i < lenval:
                out += self.term.move_left(self.columns)
                text = self.value[i][-self.columns:]
                textlen = len(text)
                out += self._color(text)

                if textlen > longest:
                    longest = textlen

        if redraw_cursor:
            if self.corner[1] is None:
                out += self.term.move_left(len(self.value[self.pos[0]]))

            out += self.redraw_cursor()

        return out

    def redraw_cursor(self):
        """
        Output sequence to restore cursor position; assumes cursor is already
        located at top-left of editor if self.corner is unset

        :rtype: str
        """

        out = ''

        # move cursor back to top left before adjusting to self.pos offset
        if self.corner[0] is not None:
            out += self.term.move_y(self.corner[0])

        if self.corner[1] is not None:
            out += self.term.move_x(self.corner[1])

        # adjust offset
        if self.pos[0] > 0:
            out += self.term.move_down(self.pos[0])

        if self.pos[1] > 0:
            out += self.term.move_right(self.pos[1])

        return out

    def process_keystroke(self, ks):
        """
        Process keystroke and produce output (if any)

        :param :class:`blessed.keyboard.Keystroke` ks: Keystroke object
            (e.g. from `inkey`)
        :returns: Updated output for the editor display
        :rtype: str
        """

        row = self.value[self.pos[0]]
        before = row[:self.pos[1]]
        after = row[self.pos[1]:]

        # TODO wrap text/cursor, overflow, up/down, tab
        if ks.code == self.term.KEY_BACKSPACE:
            if self.pos[1] == 0:
                log.debug('at start of line, nothing to backspace')
                return ''

            self.value[self.pos[0]] = before[:-1] + after
            self.pos[1] -= 1
            log.debug(f'backspace "{self.value[self.pos[0]]}" {self.pos}')

            return self._color(self.term.move_left + after + ' ' +
                               self.term.move_left(len(after) + 1))

        elif ks.code == self.term.KEY_DELETE:
            if self.pos[1] >= len(self.value[self.pos[0]]):
                log.debug('at end of line, nothing to delete')
                return ''

            after = after[1:]
            self.value[self.pos[0]] = before + after
            log.debug(f'delete "{self.value[self.pos[0]]}"')

            return self._color(after + ' ' +
                               self.term.move_left(len(after) + 1))

        elif ks.code == self.term.KEY_LEFT:
            if self.pos[1] == 0:
                log.debug('already at start of line')
                return ''

            self.pos[1] -= 1
            log.debug(f'left {self.pos}')

            return self.term.move_left

        elif ks.code == self.term.KEY_RIGHT:
            if self.pos[1] >= len(self.value[self.pos[0]]):
                log.debug('already at end of line')
                return ''

            self.pos[1] += 1
            log.debug(f'right {self.pos}')

            return self.term.move_right

        elif ks.code == self.term.KEY_HOME:
            if self.pos[1] == 0:
                log.debug('already at start of line')
                return ''

            diff = self.pos[1]
            self.pos[1] = 0
            log.debug(f'home {self.pos}')

            return self.term.move_left(diff)

        elif ks.code == self.term.KEY_END:
            strlen = len(self.value[self.pos[0]])

            if self.pos[1] >= strlen:
                log.debug('already at end of line')
                return ''

            diff = strlen - self.pos[1]
            self.pos[1] = len(self.value[self.pos[0]])
            log.debug(f'end {self.pos}')

            return self.term.move_right(diff)

        elif ks.is_sequence:
            log.debug(f'swallowing sequence {ks}')
            return ''

        elif self.pos[1] >= self.limit[1]:
            log.debug(f'reached text limit, discarding {ks}')
            return ''

        ucs = str(ks)

        if not self.term.length(ucs):
            log.debug('zero length ucs')
            return ''

        self.value[self.pos[0]] = before + ucs + after
        self.pos[1] += 1
        move_left = len(after) if self.pos[1] < len(self.value[self.pos[0]]) \
            else len(after) - 1
        log.debug(f"{self.pos}\n{self.value}")

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
