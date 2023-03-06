# stdlib
from typing import Literal

# local
from ...terminal.proxy_terminal import ProxyTerminal
from .block import BlockEditor


class LineEditor(BlockEditor):

    """Line editor (single line)"""

    def __init__(
        self, term: ProxyTerminal, columns: int, limit=0, *args, **kwargs
    ):
        """
        Line editor (single line)

        Args:
            term: The terminal to use for generating output sequences.
            columns: The width of the editor in columns.
            limit: The maximum number of characters allowed in the editor.
            args: Arguments passed to the underlying `BlockEditor` constructor.
            kwargs: Arguments passed to the underlying `BlockEditor`
                constructor.
        """

        super().__init__(term, 1, columns, limit=(limit, 1), *args, **kwargs)

    @property
    def rows(self) -> Literal[1]:
        """A line editor only has a single row."""

        return 1

    @rows.setter
    def rows(self, val: int):
        if val != 1:
            raise ValueError("LineEditor must have exactly 1 row")
