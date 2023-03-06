"""Coroutine utility methods"""

# type checking
from typing import Any, Coroutine

# stdlib
from asyncio import new_event_loop


def run_coroutine(f: Coroutine[Any, Any, Any]):
    """Helper for asynchronous method calls from synchronous code."""

    loop = new_event_loop()

    try:
        return loop.run_until_complete(f)
    finally:
        loop.close()
