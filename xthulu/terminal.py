# stdlib
from asyncio import wait_for
from asyncio.futures import TimeoutError
import functools
from time import time
# 3rd party
from blessed import Terminal
from blessed.keyboard import resolve_sequence

class AsyncTerminal(Terminal):

    def __init__(self, keyboard, *args, **kwargs):
        self.keyboard = keyboard
        super().__init__(*args, **kwargs)

    async def inkey(self, timeout=None, esc_delay=0.35):
        resolve = functools.partial(resolve_sequence,
                                    mapper=self._keymap,
                                    codes=self._keycodes)

        ucs = ''

        while not self.keyboard.empty():
            ucs += await self.keyboard.get()

        ks = resolve(text=ucs)

        if not ks:
            if timeout is None:
                ucs += await self.keyboard.get()
            else:
                try:
                    ucs += await wait_for(self.keyboard.get(), timeout=timeout)
                except TimeoutError:
                    return None

        ks = resolve(text=ucs)

        if ks.code == self.KEY_ESCAPE:
            while ucs in self._keymap_prefixes:
                try:
                    ucs += await wait_for(self.keyboard.get(),
                                          timeout=esc_delay)
                except TimeoutError:
                    break

            ks = resolve(text=ucs)

        for key in ucs[len(ks):]:
            self.keyboard.put_nowait(key)

        return ks
