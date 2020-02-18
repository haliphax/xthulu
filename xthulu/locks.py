"xthulu shared locks"

# stdlib
from contextlib import contextmanager
# local
from . import log


class Locks(object):
    _locks = {}
    _owned = {}

    @staticmethod
    def get(owner, name):
        "Acquire and hold lock on behalf of user/system"

        log.debug('{} getting lock {}'.format(owner, name))

        if name in Locks._locks:
            log.debug('{} lock already exists'.format(name))

            return False

        Locks._locks[name] = True
        owned = set([])

        if owner in Locks._owned:
            owned = Locks._owned[owner]

        owned.add(name)
        Locks._owned[owner] = owned

        return True

    @staticmethod
    def release(owner, name):
        "Release a lock owned by user/system"

        log.debug('{} releasing lock {}'.format(owner, name))

        if name not in Locks._locks:
            log.debug('{} lock does not exist'.format(name))

            return False

        if owner not in Locks._owned or name not in Locks._owned[owner]:
            log.debug('{} does not own lock {}'.format(owner, name))

            return False

        del Locks._locks[name]
        owned = Locks._owned[owner]
        owned.remove(name)
        Locks._owned[owner] = owned

        return True

    @staticmethod
    @contextmanager
    def hold(owner, name):
        "Session-agnostic lock context manager"

        try:
            yield Locks.get(owner, name)
        finally:
            Locks.release(owner, name)

    @staticmethod
    def expire(owner):
        "Remove all locks owned by user"

        log.debug('Releasing locks owned by {}'.format(owner))

        if owner not in Locks._owned or not len(Locks._owned[owner]):
            log.debug('No locks for {}'.format(owner))

            return

        locks = [l for l in Locks._owned[owner] if l in Locks._locks]

        for l in locks:
            log.debug('Releasing lock {}'.format(l))
            del Locks._locks[l]
