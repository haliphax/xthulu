"""xthulu shared locks"""

# stdlib
from contextlib import contextmanager
from functools import partial

# local
from . import log


class Locks:

    """Lock storage singleton"""

    locks: set[str] = set([])
    """Existing locks"""

    owned: dict[str, set[str]] = {}


def get(owner: str, name: str) -> bool:
    """
    Acquire and hold lock on behalf of user/system.

    Args:
        owner: The name of the owner.
        name: The name of the lock.

    Returns:
        Whether or not the lock was granted.
    """

    log.debug(f"{owner} getting lock {name}")

    if name in Locks.locks:
        log.debug(f"{name} lock already exists")

        return False

    Locks.locks.add(name)
    owned = set([])

    if owner in Locks.owned:
        owned = Locks.owned[owner]

    owned.add(name)
    Locks.owned[owner] = owned

    return True


def release(owner: str, name: str) -> bool:
    """
    Release a lock owned by user/system.

    Args:
        owner: The name of the owner.
        name: The name of the lock.

    Returns:
        Whether or not the lock was valid to begin with.
    """

    log.debug(f"{owner} releasing lock {name}")

    if name not in Locks.locks:
        log.debug(f"{name} lock does not exist")

        return False

    if owner not in Locks.owned or name not in Locks.owned[owner]:
        log.debug(f"{owner} does not own lock {name}")

        return False

    Locks.locks.remove(name)
    owned = Locks.owned[owner]
    owned.remove(name)
    Locks.owned[owner] = owned

    return True


@contextmanager
def hold(owner: str, name: str):
    """
    Session-agnostic lock context manager.

    Args:
        owner: The name of the owner.
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
    Remove all locks owned by user.

    Args:
        owner: The name of the owner.
    """

    log.debug(f"Releasing locks owned by {owner}")

    if owner not in Locks.owned:
        log.debug(f"No lock storage for {owner}")
        return

    owned: set[str] = Locks.owned[owner].copy()

    if not owned:
        log.debug(f"No remaining locks for {owner}")
    else:
        map(partial(release, (owner,)), owned)

    del Locks.owned[owner]
