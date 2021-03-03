"Asyncio blessed.Terminal implementation"

# significant rewrites for blessed functionality thanks to
# https://github.com/jquast

# stdlib
from asyncio.queues import Queue
import io
import asyncio as aio
import contextlib
from functools import partial
from multiprocessing.connection import Connection
import os
from typing import Callable
# 3rd party
import blessed
import wrapt
# local
from . import config, log
from .exceptions import ProcessClosing

debug_term = bool(config.get('debug', {}).get('term', False))


class SubprocessTerminal(blessed.Terminal):

    def __init__(self, kind: str, height: int = 0, width: int = 0,
                 pixel_height: int = 0, pixel_width: int = 0):
        stream = io.StringIO()
        super().__init__(kind, stream, force_styling=True)
        log.debug(f'Terminal.errors: {self.errors}')
        self._keyboard_fd = 'defunc'
        self._height = height
        self._width = width
        self.resolve = partial(blessed.keyboard.resolve_sequence,
                               mapper=self._keymap,
                               codes=self._keycodes)

    @contextlib.contextmanager
    def raw(self):
        yield

    @contextlib.contextmanager
    def cbreak(self):
        yield

    @property
    def is_a_tty(self):
        return True


class TerminalProxyCall(wrapt.ObjectProxy):
    def __init__(self, wrapped: Callable, attr: str, pipe_master: Connection):
        super().__init__(wrapped)
        self.pipe_master = pipe_master
        self.attr = attr

    def __call__(self, *args, **kwargs):
        self.pipe_master.send((f'!CALL{self.attr}', args, kwargs))

        return self.pipe_master.recv()


class ProxyTerminal(object):
    _kbdbuf = []

    # context manager attribs
    _ctxattrs = ('location', 'keypad', 'raw', 'cbreak', 'hidden_cursor',
                 'fullscreen')

    def __init__(self, stdin: Queue, stdout: Queue, encoding: str,
                 pipe_master: Connection, width: int = 0, height: int = 0,
                 pixel_width: int = 0, pixel_height: int = 0):
        self.stdin, self.stdout = stdin, stdout
        self.encoding = encoding
        self.pipe_master = pipe_master
        self._width = width
        self._height = height
        self._pixel_width = pixel_width
        self._pixel_height = pixel_height

    def __getattr__(self, attr: str):

        @contextlib.contextmanager
        def proxy_contextmanager(*args, **kwargs):
            # we send special '!CTX' header, which means we
            # expect two replies, the __enter__ and __exit__. because
            # context managers can be wrapped, and entry/exit can happen
            # in like entry/entry/entry/exit/exit/exit order, we *prefetch*
            # any exit value and return code -- woah! not a problem because
            # the things we wrap are pretty basic
            self.pipe_master.send((f'!CTX{attr}', args, kwargs))

            # one of two items, the '__enter__' context,
            enter_side_effect, enter_value = self.pipe_master.recv()
            exit_side_effect = self.pipe_master.recv()

            if debug_term:
                log.debug(f'wrap_ctx_manager({attr}, *{args}, **{kwargs}) '
                          f'=> entry: {enter_side_effect}, {enter_value})')
                log.debug(f'wrap_ctx_manager({attr}, *{args}, **{kwargs}) '
                          f'=> exit: {exit_side_effect}')

            if enter_side_effect:
                self.stdout.write(enter_side_effect)

            yield enter_value

            if exit_side_effect:
                self.stdout.write(exit_side_effect)

        if attr in self._ctxattrs:
            return proxy_contextmanager

        blessed_attr = getattr(blessed.Terminal, attr, None)

        if callable(blessed_attr):
            if debug_term:
                log.debug(f'{attr} callable')

            resolved_value = TerminalProxyCall(blessed_attr, attr,
                                               self.pipe_master)

            if debug_term:
                log.debug(f'value: {resolved_value!r}')
        else:
            if debug_term:
                log.debug(f'{attr} not callable')

            self.pipe_master.send((attr, (), {}))
            resolved_value = self.pipe_master.recv()

            if debug_term:
                log.debug(f'value: {resolved_value!r}')

            if isinstance(resolved_value,
                          (blessed.formatters.ParameterizingString,
                           blessed.formatters.FormattingOtherString)):
                resolved_value = TerminalProxyCall(resolved_value, attr,
                                                   self.pipe_master)
                if debug_term:
                    log.debug(repr(resolved_value))

        if debug_term:
            log.debug(f'setattr {attr}')

        setattr(self, attr, resolved_value)

        return resolved_value

    def does_styling(self):
        return True

    @property
    def pixel_width(self):
        return self._pixel_width

    @property
    def pixel_height(self):
        return self._pixel_height

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    async def inkey(self, timeout: float = None, esc_delay: float = 0.35):
        ucs = ''

        # get anything currently in kbd buffer
        for c in self._kbdbuf:
            ucs += c

        self._kbdbuf = []
        ks = (self.resolve(text=ucs) if len(ucs)
              else blessed.keyboard.Keystroke())

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

                except aio.streams.IncompleteReadError:
                    raise ProcessClosing()

                except aio.futures.TimeoutError:
                    if timeout is not None:
                        break

            ks = (self.resolve(text=ucs) if len(ucs)
                  else blessed.keyboard.Keystroke())

        if ks.code == self.KEY_ESCAPE:
            # esc was received; let's see if we're getting a key sequence
            while ucs in self._keymap_prefixes:
                try:
                    inp = await aio.wait_for(self.stdin.get(), esc_delay)
                    ucs += inp.decode(self.encoding)

                except aio.streams.IncompleteReadError:
                    raise ProcessClosing()

                except aio.futures.TimeoutError:
                    break

            ks = self.resolve(text=ucs) if len(ucs) else blessed.Keystroke()

        # append any remaining input back into the kbd buffer
        for c in ucs[len(ks):]:
            self._kbdbuf.append(c)

        return ks


def terminal_process(termtype: str, w: int, h: int, pw: int, ph: int,
                     subproc_pipe: Connection):
    """
    Avoid Python curses singleton bug by stuffing Terminal in a subprocess
    and proxying calls/responses via Pipe
    """

    subproc_term = SubprocessTerminal(termtype, w, h, pw, ph)

    while True:
        try:
            given_attr, args, kwargs = subproc_pipe.recv()
        except KeyboardInterrupt:
            return

        if debug_term:
            log.debug(f'proxy received: {given_attr}, {args!r}, '
                      f'{kwargs!r}')

        # exit sentinel
        if given_attr is None:
            if debug_term:
                log.debug(f'term={subproc_term}/pid={os.getpid()} exit')

            break

        # special attribute -- a context manager, enter it naturally, exit
        # unnaturally (even, prematurely), with the exit value ready for
        # our client side, this is only possible because blessed doesn't
        # use any state or time-sensitive values, only terminal sequences,
        # and these CM's are the only ones without side-effects.
        if given_attr.startswith('!CTX'):
            # here, we feel the real punishment of side-effects...
            sideeffect_stream = subproc_term.stream.getvalue()
            assert not sideeffect_stream, ('should be empty',
                                           sideeffect_stream)

            given_attr = given_attr[len('!CTX'):]

            if debug_term:
                log.debug(f'context attr: {given_attr}')

            with getattr(subproc_term, given_attr)(*args, **kwargs) \
                    as enter_result:
                enter_side_effect = subproc_term.stream.getvalue()
                subproc_term.stream.truncate(0)
                subproc_term.stream.seek(0)

                if debug_term:
                    log.debug('enter_result, enter_side_effect = '
                              f'{enter_result!r}, {enter_side_effect!r}')

                subproc_pipe.send((enter_result, enter_side_effect))

            exit_side_effect = subproc_term.stream.getvalue()
            subproc_term.stream.truncate(0)
            subproc_term.stream.seek(0)
            subproc_pipe.send(exit_side_effect)

        elif given_attr.startswith('!CALL'):
            given_attr = given_attr[len('!CALL'):]
            matching_attr = getattr(subproc_term, given_attr)

            if debug_term:
                log.debug(f'callable attr: {given_attr}')

            subproc_pipe.send(matching_attr(*args, **kwargs))

        else:
            if debug_term:
                log.debug(f'attr: {given_attr}')

            assert len(args) == len(kwargs) == 0, (args, kwargs)
            matching_attr = getattr(subproc_term, given_attr)

            if debug_term:
                log.debug(f'value: {matching_attr!r}')

            subproc_pipe.send(matching_attr)
