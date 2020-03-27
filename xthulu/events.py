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

    async def poll(self, event_name=None, flush=False):
        """
        Check for event

        :param str event_name: (Optional) The event name to check for
        :retval: :class:`xthulu.structs.EventData`
        :returns: The event (or None if no event was found)
        """

        popped = []
        found = None

        while not self._q.empty() and (found is None or flush):
            recv = await self._q.get()

            if recv.name == event_name or event_name is None:
                if found is None:
                    found = recv
                elif not flush:
                    popped.append(recv)
            else:
                popped.append(recv)

        # put back any events that were skipped
        map(self._q.put_nowait, popped)

        return found

    async def flush(self, event_name=None):
        """
        Flush the event queue

        :param str event_name: The event name to filter (if any)
        """

        await self.poll(event_name=event_name, flush=True)


async def put_global(event):
    """
    Put an event in every connected session's event queue

    :param :class:`xthulu.structs.EventData` event: The event to replicate
    """

    for q in EventQueues.q:
        await q.put(event)
