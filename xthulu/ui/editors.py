"editors module"


class BlockEditor(object):

    "Block editor (multiple lines)"

    #: Editor text
    value = ''
    #: Text length limit
    limit = 0
    #: Cursor position
    pos = (0, 0)

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

        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

        self._color = getattr(term, self._color_str)

    @property
    def color(self):
        "Color property; setting it also sets the internal Terminal callable"

        return getattr(self.term, self._color_str)

    @color.setter
    def color(self, val):
        self._color_str = val
        self._color = getattr(self.term, val)

    def redraw(self):
        "Output sequence to redraw editor"

        out = ''
        split = self.value.split('\r\n')
        txtlen = len(split)

        for i in range(self.rows):
            if i > 0:
                out += '\r\n'

            out += self._color(' ' * self.width)

            if i < txtlen:
                out += self.term.move_left() * self.width
                out += self._color(split[i][-self.width:])

        return out

    def redraw_cursor(self):
        """
        Output sequence to restore cursor position; assumes cursor is already
        located at top-left of editor
        """

        return (self.term.move_down(self.pos[0]) +
                self.term.move_right(self.pos[1]))

    def process_keystroke(self, ks):
        "Process keystroke and produce output (if any)"

        if ks.code == self.term.KEY_BACKSPACE and len(self.value):
            self.value = self.value[:-1]

            return (self.term.move_left() + self._color(' ')
                    + self.term.move_left())

        if ks.is_sequence:
            return

        ucs = str(ks)
        self.value += ucs

        return self._color(ucs)


class LineEditor(BlockEditor):

    "Line editor (single line)"

    def __init__(self, term, width, *args, **kwargs):
        super().__init__(term, 1, width, *args, **kwargs)

    @property
    def rows(self):
        # always 1 row
        return 1

    @rows.setter
    def rows(self, val):
        # immutable
        pass
