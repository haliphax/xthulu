"""
Asyncio blessed.Terminal implementation

Significant rewrites for blessed functionality thanks to
https://github.com/jquast
"""

# stdlib
from multiprocessing.connection import Connection
import os

# local
from ..configuration import get_config
from ..logger import log
from .subprocess import SubprocessTerminal

debug_term = bool(get_config("debug.term", False))
"""Whether terminal debugging is enabled"""


def terminal_process(
    termtype: str, w: int, h: int, pw: int, ph: int, subproc_pipe: Connection
):
    """
    Avoid Python curses singleton bug by stuffing Terminal in a subprocess
    and proxying calls/responses via Pipe.

    Args:
        termtype: The terminal type.
        w: The width in columns.
        h: The height in rows.
        pw: The width in pixels.
        ph: The height in pixels.
        subproc_pipe: The subprocess pipe for communication.
    """

    subproc_term = SubprocessTerminal(termtype, w, h, pw, ph)

    while True:
        try:
            given_attr, args, kwargs = subproc_pipe.recv()
        except KeyboardInterrupt:
            return

        if debug_term:
            log.debug(f"proxy received: {given_attr}, {args!r}, " f"{kwargs!r}")

        # exit sentinel
        if given_attr is None:
            if debug_term:
                log.debug(f"term={subproc_term}/pid={os.getpid()} exit")

            break

        # special attribute -- a context manager, enter it naturally, exit
        # unnaturally (even, prematurely), with the exit value ready for
        # our client side, this is only possible because blessed doesn't
        # use any state or time-sensitive values, only terminal sequences,
        # and these CM's are the only ones without side-effects.
        if given_attr.startswith("!CTX"):
            # here, we feel the real punishment of side-effects...
            sideeffect_stream = subproc_term.stream.getvalue()  # type: ignore
            assert not sideeffect_stream, ("should be empty", sideeffect_stream)

            given_attr = given_attr[len("!CTX") :]

            if debug_term:
                log.debug(f"context attr: {given_attr}")

            with getattr(subproc_term, given_attr)(
                *args, **kwargs
            ) as enter_result:
                enter_side_effect = (
                    subproc_term.stream.getvalue()  # type: ignore
                )
                subproc_term.stream.truncate(0)
                subproc_term.stream.seek(0)

                if debug_term:
                    log.debug(
                        "enter_result, enter_side_effect = "
                        f"{enter_result!r}, {enter_side_effect!r}"
                    )

                subproc_pipe.send((enter_result, enter_side_effect))

            exit_side_effect = subproc_term.stream.getvalue()  # type: ignore
            subproc_term.stream.truncate(0)
            subproc_term.stream.seek(0)
            subproc_pipe.send(exit_side_effect)

        elif given_attr.startswith("!CALL"):
            given_attr = given_attr[len("!CALL") :]
            matching_attr = getattr(subproc_term, given_attr)

            if debug_term:
                log.debug(f"callable attr: {given_attr}")

            subproc_pipe.send(matching_attr(*args, **kwargs))

        else:
            if debug_term:
                log.debug(f"attr: {given_attr}")

            assert len(args) == len(kwargs) == 0, (args, kwargs)
            matching_attr = getattr(subproc_term, given_attr)

            if debug_term:
                log.debug(f"value: {matching_attr!r}")

            subproc_pipe.send(matching_attr)
