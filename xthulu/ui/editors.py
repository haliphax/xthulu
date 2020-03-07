"editors module"


class BlockEditor(object):

    "Block editor (multiple lines)"

    #: Editor text
    value = []
    #: Text length limit
    limit = 0
    #: Cursor position
    pos = [0, 0]

    # internals
    _color_str = 'bold_white_on_blue'
    _color = None

    def __init__(self, term, rows, width, **kwargs):
        #: Terminal to use for sequences
        self.term = term
        #: Height in rows
        self.rows = rows
        #: Width of editor field
        self.width = width

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
        "Color property; setting it also sets the internal Terminal callable"

        return getattr(self.term, self._color_str)

    @color.setter
    def color(self, val):
        self._color_str = val
        self._color = getattr(self.term, val)

    def redraw(self, redraw_cursor=True):
        """
        Output sequence to redraw editor

        :param bool redraw_cursor: Redraw cursor position as well
        """

        out = ''
        lenval = len(self.value)
        longest = 0

        for i in range(self.rows):
            if i > 0:
                out += '\r\n'

            out += self._color(' ' * self.width)

            if i < lenval:
                out += self.term.move_left() * self.width
                text = self.value[i][-self.width:]
                textlen = len(text)
                out += self._color(text)

                if textlen > longest:
                    longest = textlen

        if redraw_cursor:
            if self.rows > 1:
                out += self.term.move_up() * self.rows

            if longest > 0:
                out += self.term.move_left() * (longest + 1)

            out += self.redraw_cursor()

        return out

    def redraw_cursor(self):
        """
        Output sequence to restore cursor position; assumes cursor is already
        located at top-left of editor
        """

        out = ''

        if self.pos[0] > 0:
            out += self.term.move_down() * self.pos[0]

        if self.pos[1] > 0:
            out += self.term.move_right() * self.pos[1]

        return out

    def process_keystroke(self, ks):
        "Process keystroke and produce output (if any)"

        row = self.value[self.pos[0]]
        before = row[:self.pos[1]]
        after = row[self.pos[1]:]

        # TODO wrap text/cursor, overflow, up/down, home, end, insert mode,
        # tab, length limit enforcement
        if ks.code == self.term.KEY_BACKSPACE:
            if self.pos[1] == 0:
                return ''

            self.value[self.pos[0]] = before[:-1] + after
            self.pos[1] -= 1

            return self._color(self.term.move_left() + after + ' ' +
                               (self.term.move_left() * (len(after) + 1)))

        elif ks.code == self.term.KEY_DELETE:
            if self.pos[1] >= len(self.value[self.pos[0]]):
                return ''

            after = after[1:]
            self.value[self.pos[0]] = before + after

            return self._color(after + ' ' +
                               (self.term.move_left() * (len(after) + 1)))

        elif ks.code == self.term.KEY_LEFT:
            if self.pos[1] == 0:
                return ''

            self.pos[1] -= 1

            return self.term.move_left()

        elif ks.code == self.term.KEY_RIGHT:
            if self.pos[1] >= len(self.value[self.pos[0]]):
                return ''

            self.pos[1] += 1

            return self.term.move_right()

        elif ks.is_sequence:
            return ''

        ucs = str(ks)

        if not self.term.length(ucs):
            return ''

        self.value[self.pos[0]] = before + ucs + after
        self.pos[1] += 1

        return self._color(ucs + after + (self.term.move_left() * len(after)))


class LineEditor(BlockEditor):

    "Line editor (single line)"

    def __init__(self, term, width, *args, **kwargs):
        super().__init__(term, 1, width, *args, **kwargs)

    @property
    def rows(self):
        "Always 1 row"
        return 1

    @rows.setter
    def rows(self, val):
        pass
