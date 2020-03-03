"Asyncio blessed.Terminal implementation"

# stdlib
import asyncio as aio
from contextlib import contextmanager
from functools import partial
# 3rd party
from blessed import Terminal as BlessedTerminal
from blessed.keyboard import Keystroke, resolve_sequence
# local
from . import config, log
from .exceptions import ProcessClosing

# TODO tty methods (at least height, width), get size from asyncssh

debug_proxy = (config['debug']['proxy'] if 'debug' in config
               and 'proxy' in config['debug']
               else False)


class Terminal(BlessedTerminal):

    def __init__(self, kind, stream):
        super().__init__(kind, stream, force_styling=True)
        self._keyboard_fd = 'defunc'
        self.resolve = partial(resolve_sequence, mapper=self._keymap,
                               codes=self._keycodes)

    @contextmanager
    def raw(self):
        yield

    @contextmanager
    def cbreak(self):
        yield

    @property
    def is_a_tty(self):
        return True


class TerminalProxy(object):

    _kbdbuf = []
    # Terminal attributes that do not accept paramters must be treated
    # specially, or else they have to be called like term.normal() everywhere
    _fixattrs = ('clear_eol', 'normal',)

    def __init__(self, stdin, encoding, proxy_in, proxy_out, width=0,
                 height=0):
        self.encoding = encoding
        self._stdin = stdin
        self._in = proxy_in
        self._out = proxy_out
        self._width = width
        self._height = height
        # pre-load a few attributes so we don't have to query them from the
        # proxy every single time we use them (i.e., in loops)
        self._keymap_prefixes = self._keymap_prefixes()

    def __getattr__(self, attr):
        def wrap(*args, **kwargs):
            self._in.send((attr, args, kwargs))
            out = self._in.recv()

            if debug_proxy:
                log.debug('proxy result {}: {}'.format(attr, out))

            return out

        if debug_proxy:
            log.debug('wrapping {} for proxy'.format(attr))

        a = None

        try:
            a = getattr(AsyncTerminal, attr)
        except:
            pass

        if callable(a) or attr.startswith('KEY_') or attr in self._fixattrs:
            return wrap()

        return wrap

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width

    async def inkey(self, timeout=None, esc_delay=0.35):
        ucs = ''

        # get anything currently in kbd buffer
        for c in self._kbdbuf:
            ucs += c

        self._kbdbuf = []
        ks = self.resolve(text=ucs) if len(ucs) else Keystroke()

        # either buffer was empty or we don't have enough for a keystroke;
        # wait for input from kbd
        if not ks:
            while True:
                try:
                    if timeout is None:
                        # don't actually wait indefinitely; wait in 0.1 second
                        # increments so that the coroutine can be aborted if
                        # the connection is dropped
                        ucs += ((await aio.wait_for(self._stdin.get(),
                                                    timeout=0.1))
                                 .decode(self.encoding))
                    else:
                        ucs += ((await aio.wait_for(self._stdin.get(),
                                                    timeout=timeout))
                                .decode(self.encoding))

                    break
                except aio.streams.IncompleteReadError:
                    raise ProcessClosing()
                except aio.futures.TimeoutError:
                    if timeout is not None:
                        break

            ks = self.resolve(text=ucs) if len(ucs) else Keystroke()

        if ks.code == self.KEY_ESCAPE:
            # esc was received; let's see if we're getting a key sequence
            while ucs in self._keymap_prefixes:
                try:
                    ucs += ((await aio.wait_for(self._stdin.get(),
                                                timeout=esc_delay))
                             .decode(self.encoding))
                except aio.streams.IncompleteReadError:
                    raise ProcessClosing()
                except aio.futures.TimeoutError:
                    break

            ks = self.resolve(text=ucs) if len(ucs) else Keystroke()

        # append any remaining input back into the kbd buffer
        for c in ucs[len(ks):]:
            self._kbdbuf.append(c)

        return ks
