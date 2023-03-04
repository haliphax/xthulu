"""Event queue mechanism"""

# stdlib
from collections import OrderedDict
from uuid import uuid4

# local
from .structs import EventData


class EventQueue:

    """
    Event queue which uses two underlying storage mechanisms for efficiency.
    `EventData` objects are stored in an `OrderedDict` with generated UUIDs as
    keys. These UUIDs are referred to in a chronologically-ordered list stored
    in a dict where the keys are the event names. This makes it possible to pull
    all events by using the list or to pull only events with a certain name by
    using the OrderedDict (without iterating through unrelated events).
    """

    def __init__(self, sid: str):
        self._dict: dict[str, list[str]] = {}
        self._list: OrderedDict[str, EventData] = OrderedDict()
        EventQueues.q[sid] = self

    def add(self, event: EventData):
        """
        Add an event to the queue.

        Args:
            event: The event to add.
        """

        key = str(uuid4())
        self._list[key] = event
        evlist = (
            self._dict[event.name] if event.name in self._dict.keys() else []
        )
        evlist.append(key)
        self._dict[event.name] = evlist

    def get(self, name: str | None = None, flush: bool = True):
        """
        Get an event or all events from the queue. If `name` is provided, only
        events with that name will be returned. By default, events matching the
        criteria will be flushed afterward. To preserve them, set `flush` to
        `False`.

        Args:
            name: The event name to query. If not provided, queries all events.
            flush: Whether to delete events from the queue.

        Returns:
            A list of events matching the criteria (or an empty list).
        """

        events = (
            self._list.values()
            if name is None
            else [self._list[key] for key in self._dict.get(name, [])]
        )

        if flush:
            self.flush(name)

        return events

    def flush(self, name: str | None = None):
        """
        Flush the event queue. If a name is provided, only events with that name
        will be flushed.

        Args:
            name: The event name to flush from the queue. `None` flushes all.
        """

        if name is None:
            self._list.clear()
            self._dict.clear()

            return

        keys = self._dict.get(name)

        if not keys:
            return

        for key in keys:
            del self._list[key]

        self._dict[name].clear()


class EventQueues:

    """Underlying event queue storage"""

    q: dict[str, EventQueue] = {}
    """Queue storage, mapped by session ID (sid)"""


async def put_global(event: EventData):
    """
    Put an event in every connected session's event queue.

    Args:
        event: The event to replicate.
    """

    for q in EventQueues.q.values():
        q.add(event)
