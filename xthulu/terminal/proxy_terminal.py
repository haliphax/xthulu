"""Proxied blessed.Terminal"""

# type checking
from typing import Any, Callable

# stdlib
import asyncio as aio
import contextlib
from multiprocessing.connection import Connection

# 3rd party
from blessed import Terminal
from blessed.keyboard import Keystroke
from blessed.formatters import FormattingOtherString, ParameterizingString

# local
from .. import config, log
from ..exceptions import ProcessClosing
from .proxy_call import TerminalProxyCall

debug_term = bool(config.get("debug", {}).get("term", False))
"""Whether terminal debugging is enabled"""


class ProxyTerminal:

    """
    Terminal implementation which proxies calls to a `blessed.Terminal` instance
    running in a subprocess
    """

    _kbdbuf = []

    # context manager attribs
    _ctxattrs = (
        "cbreak",
        "fullscreen",
        "hidden_cursor",
        "keypad",
        "location",
        "raw",
    )

    # their type hints
    cbreak: contextlib._GeneratorContextManager[Any]
    fullscreen: contextlib._GeneratorContextManager[Any]
    hidden_cursor: contextlib._GeneratorContextManager[Any]
    keypad: contextlib._GeneratorContextManager[Any]
    location: contextlib._GeneratorContextManager[Any]
    raw: contextlib._GeneratorContextManager[Any]

    def __init__(
        self,
        stdin: aio.Queue[bytes],
        stdout: Any,
        encoding: str,
        pipe_master: Connection,
        width: int = 0,
        height: int = 0,
        pixel_width: int = 0,
        pixel_height: int = 0,
    ):
        self.stdin, self.stdout = stdin, stdout
        self.encoding = encoding
        self.pipe_master = pipe_master
        self._width = width
        self._height = height
        self._pixel_width = pixel_width
        self._pixel_height = pixel_height

    def __getattr__(self, attr: str) -> Callable[..., str]:
        @contextlib.contextmanager
        def proxy_contextmanager(*args, **kwargs):
            # we send special '!CTX' header, which means we
            # expect two replies, the __enter__ and __exit__. because
            # context managers can be wrapped, and entry/exit can happen
            # in like entry/entry/entry/exit/exit/exit order, we *prefetch*
            # any exit value and return code -- woah! not a problem because
            # the things we wrap are pretty basic
            self.pipe_master.send((f"!CTX{attr}", args, kwargs))

            # one of two items, the '__enter__' context,
            enter_side_effect, enter_value = self.pipe_master.recv()
            exit_side_effect = self.pipe_master.recv()

            if debug_term:
                log.debug(
                    f"wrap_ctx_manager({attr}, *{args}, **{kwargs}) "
                    f"=> entry: {enter_side_effect}, {enter_value})"
                )
                log.debug(
                    f"wrap_ctx_manager({attr}, *{args}, **{kwargs}) "
                    f"=> exit: {exit_side_effect}"
                )

            if enter_side_effect:
                self.stdout.write(enter_side_effect)

            yield enter_value

            if exit_side_effect:
                self.stdout.write(exit_side_effect)

        if attr in self._ctxattrs:
            return proxy_contextmanager  # type: ignore

        blessed_attr = getattr(Terminal, attr, None)

        if callable(blessed_attr):
            if debug_term:
                log.debug(f"{attr} callable")

            resolved_value = TerminalProxyCall(
                blessed_attr, attr, self.pipe_master
            )

            if debug_term:
                log.debug(f"value: {resolved_value!r}")
        else:
            if debug_term:
                log.debug(f"{attr} not callable")

            self.pipe_master.send((attr, (), {}))
            resolved_value = self.pipe_master.recv()

            if debug_term:
                log.debug(f"value: {resolved_value!r}")

            if isinstance(
                resolved_value,
                (
                    ParameterizingString,
                    FormattingOtherString,
                ),
            ):
                resolved_value = TerminalProxyCall(
                    resolved_value, attr, self.pipe_master
                )
                if debug_term:
                    log.debug(repr(resolved_value))

        if debug_term:
            log.debug(f"setattr {attr}")

        setattr(self, attr, resolved_value)

        return resolved_value

    def does_styling(self):
        return True

    does_styling.__doc__ = Terminal.does_styling.__doc__

    @property
    def pixel_width(self):
        return self._pixel_width

    pixel_width.__doc__ = Terminal.pixel_width.__doc__

    @property
    def pixel_height(self):
        return self._pixel_height

    pixel_height.__doc__ = Terminal.pixel_height.__doc__

    @property
    def height(self):
        return self._height

    height.__doc__ = Terminal.height.__doc__

    @property
    def width(self):
        return self._width

    width.__doc__ = Terminal.width.__doc__

    async def inkey(
        self, timeout: float | None = None, esc_delay: float = 0.35
    ):
        ucs = ""

        # get anything currently in kbd buffer
        for c in self._kbdbuf:
            ucs += c

        self._kbdbuf = []
        ks: Keystroke = (
            self.resolve(text=ucs) if len(ucs) else Keystroke()
        )  # type: ignore

        # either buffer was empty or we don't have enough for a keystroke;
        # wait for input from kbd
        if not ks:
            while True:
                try:
                    if timeout is None:
                        # don't actually wait indefinitely; wait in 0.1 second
                        # increments so that the coroutine can be aborted if
                        # the connection is dropped
                        inp = await aio.wait_for(self.stdin.get(), 0.1)
                        ucs += inp.decode(self.encoding)
                    else:
                        inp = await aio.wait_for(self.stdin.get(), timeout)
                        ucs += inp.decode(self.encoding)

                    break

                except aio.IncompleteReadError:
                    raise ProcessClosing()

                except aio.TimeoutError:
                    if timeout is not None:
                        break

            ks = (
                self.resolve(text=ucs) if len(ucs) else Keystroke()
            )  # type: ignore

        if ks.code == self.KEY_ESCAPE:
            # esc was received; let's see if we're getting a key sequence
            while ucs in self._keymap_prefixes:  # type: ignore
                try:
                    inp = await aio.wait_for(self.stdin.get(), esc_delay)
                    ucs += inp.decode(self.encoding)

                except aio.IncompleteReadError:
                    raise ProcessClosing()

                except aio.TimeoutError:
                    break

            ks = (
                self.resolve(text=ucs) if len(ucs) else Keystroke()
            )  # type: ignore

        # append any remaining input back into the kbd buffer
        for c in ucs[len(ks) :]:
            self._kbdbuf.append(c)

        return ks

    inkey.__doc__ = Terminal.inkey.__doc__
