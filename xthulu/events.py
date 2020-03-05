"xthulu event queues"


class EventQueues(object):

    "Underlying event queue storage"

    q = {}


class EventQueue(object):

    "Event queue management surface"

    def __init__(self, sid):
        self._q = EventQueues.q[sid]

    def __getattr__(self, attr):
        return getattr(self._q, attr)

    async def poll(self, event_name=None):
        """
        Check for event

        :param str event_name: (Optional) The event name to check for
        :retval: :class:`xthulu.structs.EventData`
        :returns: The event (or None if no event was found)
        """

        popped = []
        found = None

        while not self._q.empty() and found is None:
            recv = await self._q.get()

            if recv.name == event_name or event_name is None:
                found = recv
            else:
                popped.append(recv)

        # put back any events that were skipped
        map(self._q.put_nowait, popped)

        return found

    async def flush(self, event_name=None):
        """
        Flush the event queue

        :param str event_name: (Optional) The event name to filter
        """

        popped = []

        while not self._q.empty():
            recv = await self._q.get()

            if event_name is not None and recv.name != event_name:
                popped.append(recv)

        # put back any events that were skipped
        map(self._q.put_nowait, popped)


async def put_global(event):
    """
    Put an event in every connected session's event queue

    :param :class:`xthulu.structs.EventData` event: The event to replicate
    """

    for q in EventQueues.q:
        await q.put(event)
