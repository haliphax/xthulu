"""Grapheme class"""

# type checking
from __future__ import annotations

# 3rd party
from wcwidth import wcswidth


class Grapheme:

    """
    Class for storing (potentially clustered) graphemes

    The base character is stored separately from its various modifying
    sequences to accommodate terminals which do not support zero-width
    characters, combining characters, etc. Variation-selected emoji which are
    considered by the terminal (incorrectly) to be narrow graphemes are flagged
    so that the column offset caused during display can be compensated for.
    """

    char: str
    mods: list[str]
    width: int
    force_width: bool

    def __init__(
        self,
        char: str = "",
        mods: list[str] | None = None,
        width: int = 1,
        force_width: bool = False,
    ):
        self.char = char
        self.mods = mods if mods else []
        self.width = width
        self.force_width = force_width

    def _modstr(self, s):
        return "0x%04X" % ord(s) if wcswidth(s) <= 0 else s

    def __eq__(self, other: Grapheme):
        return str(self) == str(other)

    def __repr__(self):
        return (
            f"Grapheme(char={self.char!r}, "
            f"mods={[self._modstr(c) for c in self.mods]}, "
            f"width={self.width}{' <forced>' if self.force_width else ''})"
        )

    def __str__(self):
        return "".join((self.raw, " " if self.force_width else ""))

    @property
    def raw(self):
        """The raw output of this grapheme, without forced-width adjustment."""

        return "".join((self.char, "".join(self.mods)))
