# stdlib
from asyncio import AbstractEventLoop, get_event_loop, new_event_loop


def loop() -> AbstractEventLoop:
    try:
        return get_event_loop()
    except RuntimeError:
        return new_event_loop()
