"""Input utilities"""

# stdlib
from asyncio import QueueEmpty, sleep, wait_for

# local
from ...context import SSHContext


async def wait_for_key(
    context: SSHContext, text="", spinner="dots", timeout=0.0
) -> bytes | None:
    """
    Wait for (and return) a keypress.

    Args:
        context: The current `xthulu.ssh.context.SSHContext`.
        text: The prompt text, if any.
        spinner: The prompt spinner (if `text` is specified).
        timeout: The length of time (in seconds) to wait for input. A value of \
            `0` will wait forever.

    Returns:
        The byte sequence of the key that was pressed, if any.
    """

    async def _wait():
        seq = []

        while True:
            try:
                key = context.input.get_nowait()
                seq.append(key)

                # wait for next char in ESC sequence (arrow keys, etc.)
                if key == b"\x1b":
                    try:
                        key = await wait_for(context.input.get(), 0.2)
                        seq.append(key)
                    except TimeoutError:
                        pass

                break

            except QueueEmpty:
                await sleep(0.01)

        return b"".join(seq)

    try:
        if text == "":
            if timeout > 0.0:
                return await wait_for(_wait(), timeout)

            return await _wait()

        with context.console.status(text, spinner=spinner):
            if timeout > 0.0:
                return await wait_for(_wait(), timeout)

            return await _wait()

    except TimeoutError:
        pass

    return None
