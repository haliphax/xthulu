# typing
from typing import Any, IO

# 3rd party
from asyncssh import SSHWriter


class FileWrapper(IO[str]):
    _encoding: str
    _wrapped: SSHWriter[Any]

    def __init__(self, wrapped: SSHWriter[Any], encoding: str):
        self._encoding = encoding
        self._wrapped = wrapped
        super().__init__()

    def write(self, string: str):
        try:
            self._wrapped.write(
                string.replace("\n", "\r\n").encode(self._encoding)
            )
        except BrokenPipeError:
            # process is likely closing
            pass
