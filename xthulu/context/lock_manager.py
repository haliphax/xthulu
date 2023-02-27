"""Context specific lock management"""

from .. import locks


class _LockManager(object):
    """Internal class for managing user locks"""

    def __init__(self, sid: str, name: str):
        self.sid = sid
        self.name = name

    def __enter__(self, *args, **kwargs):
        return locks.get(self.sid, self.name)

    def __exit__(self, *args, **kwargs):
        return locks.release(self.sid, self.name)
