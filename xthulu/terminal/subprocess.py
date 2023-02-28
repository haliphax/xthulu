"""Subprocess terminal"""

# stdlib
import contextlib
from functools import partial
from io import StringIO

# 3rd party
from blessed.keyboard import resolve_sequence
from blessed.terminal import Terminal

# local
from .. import log


class SubprocessTerminal(Terminal):

    """`blessed.Terminal` instance which runs in a subprocess"""

    def __init__(
        self,
        kind: str,
        height: int = 0,
        width: int = 0,
        pixel_height: int = 0,
        pixel_width: int = 0,
    ):
        stream = StringIO()
        super().__init__(kind, stream, force_styling=True)
        log.debug(f"Terminal.errors: {self.errors}")
        self._keyboard_fd = "defunc"
        self._height = height
        self._width = width
        self.resolve = partial(
            resolve_sequence,
            mapper=self._keymap,  # type: ignore
            codes=self._keycodes,  # type: ignore
        )

    @contextlib.contextmanager
    def raw(self):
        yield

    raw.__doc__ = Terminal.raw.__doc__

    @contextlib.contextmanager
    def cbreak(self):
        yield

    cbreak.__doc__ = Terminal.cbreak.__doc__

    @property
    def is_a_tty(self):
        return True

    is_a_tty.__doc__ = Terminal.is_a_tty.__doc__
