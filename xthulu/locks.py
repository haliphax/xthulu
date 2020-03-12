"xthulu shared locks"

# stdlib
from contextlib import contextmanager
# local
from . import log


class Locks(object):

    "Lock storage singleton"

    locks = set([])
    owned = {}


def get(owner, name):
    """
    Acquire and hold lock on behalf of user/system

    :param str owner: The name of the owner
    :param str name: The name of the lock
    :returns: Whether or not the lock was granted
    :rtype: bool
    """

    log.debug(f'{owner} getting lock {name}')

    if name in Locks.locks:
        log.debug(f'{name} lock already exists')

        return False

    Locks.locks.add(name)
    owned = set([])

    if owner in Locks.owned:
        owned = Locks.owned[owner]

    owned.add(name)
    Locks.owned[owner] = owned

    return True


def release(owner, name):
    """
    Release a lock owned by user/system

    :param str owner: The name of the owner
    :param str name: The name of the lock
    :returns: Whether or not the lock was valid to begin with
    :rtype: bool
    """

    log.debug(f'{owner} releasing lock {name}')

    if name not in Locks.locks:
        log.debug(f'{name} lock does not exist')

        return False

    if owner not in Locks.owned or name not in Locks.owned[owner]:
        log.debug(f'{owner} does not own lock {name}')

        return False

    Locks.locks.remove(name)
    owned = Locks.owned[owner]
    owned.remove(name)
    Locks.owned[owner] = owned

    return True


@contextmanager
def hold(owner, name):
    """
    Session-agnostic lock context manager

    :param str owner: The name of the owner
    :param str name: The name of the lock
    :returns: Whether or not the lock was granted
    :rtype: bool
    """

    try:
        yield get(owner, name)
    finally:
        release(owner, name)


def expire(owner):
    """
    Remove all locks owned by user

    :param str owner: The name of the owner
    """

    log.debug(f'Releasing locks owned by {owner}')
    locks = 0
    owned = None

    if owner in Locks.owned:
        owned = Locks.owned[owner].copy()
        locks = len(owned)

    if locks == 0:
        log.debug(f'No locks for {owner}')
    else:
        for l in owned:
            release(owner, l)

    if owned is not None:
        del Locks.owned[owner]
