"xthulu shared locks"

# stdlib
from contextlib import contextmanager
# local
from . import log


class Locks(object):
    locks = set([])
    owned = {}


def get(owner, name):
    "Acquire and hold lock on behalf of user/system"

    log.debug('{} getting lock {}'.format(owner, name))

    if name in Locks.locks:
        log.debug('{} lock already exists'.format(name))

        return False

    Locks.locks.add(name)
    owned = set([])

    if owner in Locks.owned:
        owned = Locks.owned[owner]

    owned.add(name)
    Locks.owned[owner] = owned

    return True


def release(owner, name):
    "Release a lock owned by user/system"

    log.debug('{} releasing lock {}'.format(owner, name))

    if name not in Locks.locks:
        log.debug('{} lock does not exist'.format(name))

        return False

    if owner not in Locks.owned or name not in Locks.owned[owner]:
        log.debug('{} does not own lock {}'.format(owner, name))

        return False

    Locks.locks.remove(name)
    owned = Locks.owned[owner]
    owned.remove(name)
    Locks.owned[owner] = owned

    return True


@contextmanager
def hold(owner, name):
    "Session-agnostic lock context manager"

    try:
        yield get(owner, name)
    finally:
        release(owner, name)


def expire(owner):
    "Remove all locks owned by user"

    log.debug('Releasing locks owned by {}'.format(owner))
    locks = 0
    owned = None

    if owner in Locks.owned:
        owned = Locks.owned[owner].copy()
        locks = len(owned)

    if locks == 0:
        log.debug('No locks for {}'.format(owner))
    else:
        for l in owned:
            release(owner, l)

    if owned is not None:
        del Locks.owned[owner]
