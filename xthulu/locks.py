"xthulu shared locks"

# stdlib
from contextlib import contextmanager
# local
from . import log


class Locks(object):
    locks = {}
    owned = {}


def get(owner, name):
    "Acquire and hold lock on behalf of user/system"

    log.debug('{} getting lock {}'.format(owner, name))

    if name in Locks.locks:
        log.debug('{} lock already exists'.format(name))

        return False

    Locks.locks[name] = True
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

    del Locks.locks[name]
    owned = Locks.owned[owner]
    owned.remove(name)
    Locks.owned[owner] = owned

    return True


@contextmanager
def hold(owner, name):
    "Session-agnostic lock context manager"

    try:
        yield Locks.get(owner, name)
    finally:
        Locks.release(owner, name)


def expire(owner):
    "Remove all locks owned by user"

    log.debug('Releasing locks owned by {}'.format(owner))

    if owner not in Locks.owned or not len(Locks.owned[owner]):
        log.debug('No locks for {}'.format(owner))

        return

    locks = [l for l in Locks.owned[owner] if l in Locks.locks]

    for l in locks:
        log.debug('Releasing lock {}'.format(l))
        del Locks.locks[l]
