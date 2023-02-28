"""xthulu unit tests"""

# type checking
from typing import Any, Coroutine

# stdlib
from asyncio import new_event_loop
import logging

logging.disable(logging.CRITICAL)


def run_coroutine(f: Coroutine[Any, Any, Any]):
    """Helper for asynchronous invocations during unit testing."""

    loop = new_event_loop()
    result = loop.run_until_complete(f)
    loop.close()
    return result
