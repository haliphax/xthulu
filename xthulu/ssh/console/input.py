"""Input utilities"""

# stdlib
from asyncio import QueueEmpty, sleep, wait_for

# local
from ..context import SSHContext


async def wait_for_key(cx: SSHContext, text="", spinner="dots", timeout=0.0):
    """Wait for (and return) a keypress."""

    async def _wait():
        seq = []

        while True:
            try:
                key = cx.input.get_nowait()
                seq.append(key)

                # wait for next char in ESC sequence (arrow keys, etc.)
                if key == b"\x1b":
                    try:
                        key = await wait_for(cx.input.get(), 0.2)
                        seq.append(key)
                    except TimeoutError:
                        pass

                    break
                else:
                    break

            except QueueEmpty:
                await sleep(0.01)

        return b"".join(seq)

    try:
        if text == "":
            if timeout > 0.0:
                return await wait_for(_wait(), timeout)

            return await _wait()

        with cx.term.status(text, spinner=spinner):
            if timeout > 0.0:
                return await wait_for(_wait(), timeout)

            return await _wait()

    except TimeoutError:
        pass
