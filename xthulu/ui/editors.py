"editors module"


class BlockEditor(object):

    "Block editor (multiple lines)"

    #: X coordinate
    x = None
    #: Y coordinate
    y = None
    #: Text length limit
    limit = 0
    #: Text
    text = ''

    def __init__(self, term, rows, width, **kwargs):
        #: Terminal to use for sequences
        self.term = term
        #: Height in rows
        self.rows = rows
        #: Width of editor field
        self.width = width

        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

    def refresh(self):
        out = ''

        if self.x is not None and self.y is not None:
            out += self.term.move(self.x, self.y)
        elif self.x is not None:
            out += self.term.move_x(self.x)
        elif self.y is not None:
            out += self.term.move_y(self.y)

        out += (self.term.on_blue(' ' * (self.width))
                + self.term.move_left(self.width)
                + self.term.bold_white_on_blue(self.text))

        return out

    def process_keystroke(self, ks):
        if ks.is_sequence:
            return

        ucs = str(ks)
        self.text += ucs

        return self.term.bold_white_on_blue(ucs)


class LineEditor(BlockEditor):

    "Line editor (single line)"

    def __init__(self, term, width, x=None, y=None):
        super().__init__(term, 1, width, x=x, y=y)

    @property
    def rows(self):
        return 1

    @rows.setter
    def rows(self, val):
        pass
