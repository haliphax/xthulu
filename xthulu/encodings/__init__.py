"encodings module"


def register_encodings():
    # stdlib
    from codecs import decode, register

    # local
    from . import cp437

    _encodings = {
        "cp437": cp437.getregentry(),
    }

    def _search_function(encoding: str):
        if encoding not in _encodings:
            return None

        return _encodings[encoding]

    register(_search_function)

    for c in ("cp437",):
        decode(bytes((27,)), c)
