"""Encodings module"""

# stdlib
from codecs import decode, register

# local
from . import amiga, cp437


def register_encodings():
    """Register encodings to be used by the system."""

    _encodings = {
        "amiga": amiga.getregentry(),
        "cp437": cp437.getregentry(),
    }

    def _search_function(encoding: str):
        if encoding not in _encodings:
            return None

        return _encodings[encoding]

    register(_search_function)

    for c in (
        "amiga",
        "cp437",
    ):
        decode(bytes((27,)), c)
