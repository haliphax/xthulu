"editors module"


class BlockEditor(object):

    "Block editor (multiple lines)"

    #: Text length limit
    limit = 0
    #: Text
    text = ''
    #: Cursor position
    pos = (0, 0)

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
        split = self.text.split('\r\n')
        txtlen = len(split)

        for i in range(max(txtlen, self.rows)):
            if i > 0:
                out += '\r\n'

            out += self.term.on_blue(' ' * self.width)

            if i < txtlen:
                out += self.term.move_left() * self.width
                out += self.term.bold_white_on_blue(
                        split[i][-self.width:])

        return out

    def process_keystroke(self, ks):
        if ks.code == self.term.KEY_BACKSPACE and len(self.text):
            self.text = self.text[:-1]

            return (self.term.move_left() + self.term.bold_white_on_blue(' ')
                    + self.term.move_left())

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
