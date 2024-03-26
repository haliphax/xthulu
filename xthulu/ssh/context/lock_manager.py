"""Context specific lock management"""

# local
from ...locks import get, release


class _LockManager:
    """Internal class for managing user locks"""

    def __init__(self, sid: str, name: str):
        self.sid = sid
        self.name = name

    def __enter__(self, *args, **kwargs):
        return get(self.sid, self.name)

    def __exit__(self, *args, **kwargs):
        return release(self.sid, self.name)
