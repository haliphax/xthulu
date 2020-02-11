"Asyncio blessed.Terminal implementation"

# stdlib
from asyncio import wait_for
from asyncio.futures import TimeoutError
import functools
from time import time
# 3rd party
from blessed import Terminal
from blessed.keyboard import resolve_sequence
# local
from .exceptions import ProcessClosingException

# TODO tty methods (at least cbreak, height, width), get size from asyncssh


class AsyncTerminal(Terminal):

    def __init__(self, keyboard, proc, yield_func, *args, **kwargs):
        self._kbd = keyboard
        self._proc = proc
        self._yield = yield_func
        super().__init__(*args, **kwargs)

    async def inkey(self, timeout=None, esc_delay=0.35):
        resolve = functools.partial(resolve_sequence,
                                    mapper=self._keymap,
                                    codes=self._keycodes)
        ucs = ''

        # get anything currently in kbd buffer
        while not self._kbd.empty():
            ucs += await self._kbd.get()

        ks = resolve(text=ucs)

        # either buffer was empty or we don't have enough for a keystroke;
        # wait for input from kbd
        if not ks:
            if timeout is None:
                # don't actually wait indefinitely; wait in 0.1 second
                # increments so that the coroutine can be aborted if the
                # connection is dropped and events can be processed by
                # the yield function
                while True:
                    try:
                        await self._yield()
                        ucs += await wait_for(self._kbd.get(), timeout=0.1)

                        break
                    except TimeoutError:
                        if self._proc.is_closing():
                            raise ProcessClosingException()

                        continue
            else:
                try:
                    await self._yield()
                    ucs += await wait_for(self._kbd.get(), timeout=timeout)
                except TimeoutError:
                    return None

            ks = resolve(text=ucs)

        if ks.code == self.KEY_ESCAPE:
            # esc was received; let's see if we're getting a key sequence
            while ucs in self._keymap_prefixes:
                try:
                    ucs += await wait_for(self._kbd.get(), timeout=esc_delay)
                except TimeoutError:
                    break

            ks = resolve(text=ucs)

        # push any remaining input back into the kbd buffer
        for key in ucs[len(ks):]:
            await self._kbd.put(key)

        return ks
