"""Terminal proxy call wrapper"""

# type checking
from typing import Callable

# stdlib
from multiprocessing.connection import Connection

# 3rd party
from wrapt import ObjectProxy


class TerminalProxyCall(ObjectProxy):
    """Wrapped terminal call to be proxied"""

    def __init__(self, wrapped: Callable, attr: str, pipe_master: Connection):
        super().__init__(wrapped)
        self.pipe_master = pipe_master
        self.attr = attr

    def __call__(self, *args, **kwargs):
        self.pipe_master.send((f"!CALL{self.attr}", args, kwargs))

        return self.pipe_master.recv()
