"""Shared lock semaphore methods"""

# stdlib
from contextlib import contextmanager

# 3rd party
from redis.lock import Lock

# local
from .resources import Resources
from .logger import log

cache = Resources().cache


class _Locks:

    """Internal lock storage mechanism"""

    locks: dict[str, dict[str, Lock]] = {}
    """Mapping of lock keys to lock objects"""


def get(owner: str, name: str) -> bool:
    """
    Acquire and hold lock on behalf of user/system.

    Args:
        owner: The sid of the owner.
        name: The name of the lock.

    Returns:
        Whether or not the lock was granted.
    """

    log.debug(f"{owner} acquiring lock {name}")
    lock = cache.lock(f"locks.{name}", thread_local=False)

    if not lock.acquire(blocking=False):
        log.debug(f"{owner} failed to acquire lock {name}")

        return False

    log.debug(f"{owner} acquired lock {name}")
    locks = _Locks.locks[owner] if owner in _Locks.locks else {}
    locks[name] = lock
    _Locks.locks[owner] = locks

    return True


def release(owner: str, name: str) -> bool:
    """
    Release a lock owned by user/system.

    Args:
        owner: The sid of the owner.
        name: The name of the lock.

    Returns:
        Whether or not the lock was valid to begin with.
    """

    log.debug(f"{owner} releasing lock {name}")
    locks = _Locks.locks[owner] if owner in _Locks.locks else {}

    if not locks:
        log.debug(f"{owner} failed to release lock {name}; no locks owned")

        return False

    if name not in locks:
        log.debug(f"{owner} failed to release lock {name}; not owned")

        return False

    lock = locks[name]

    if not lock.locked():
        log.debug(f"{owner} failed to release lock {name}; not locked")

        return False

    lock.release()
    log.debug(f"{owner} released lock {name}")
    del locks[name]

    if not locks:
        del _Locks.locks[owner]
    else:
        _Locks.locks[owner] = locks

    return True


@contextmanager
def hold(owner: str, name: str):
    """
    Session-agnostic lock context manager.

    Args:
        owner: The sid of the owner.
        name: The name of the lock.

    Returns:
        Whether or not the lock was granted.
    """

    try:
        yield get(owner, name)
    finally:
        release(owner, name)


def expire(owner: str):
    """
    Remove all locks owned by user for this connection.

    Args:
        owner: The sid of the owner.
    """

    log.debug(f"Releasing locks owned by {owner}")
    locks = _Locks.locks[owner] if owner in _Locks.locks else {}

    if not locks:
        log.debug(f"No locks owned by {owner}")

        return

    for lock in locks.copy():
        release(owner, lock)
