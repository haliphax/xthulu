"xthulu event queues"

# local
from .structs import EventData


class EventQueues(object):
    "Underlying event queue storage"

    q = {}


class EventQueue(object):
    "Event queue management surface"

    def __init__(self, sid: str):
        self._q = EventQueues.q[sid]

    def __getattr__(self, attr: str):
        return getattr(self._q, attr)

    async def poll(
        self, event_name: str = None, flush=False, get_last=False
    ) -> EventData:
        """
        Check for event

        :param event_name: The event name to check for (if any)
        :param flush: If other events with the same name should be removed
        :param get_last: To return the last match rather than the first
        :returns: The event (or None if no event was found)
        """

        popped = []
        found: EventData = None
        last: EventData = None

        while not self._q.empty() and (found is None or flush or get_last):
            recv = await self._q.get()

            if recv.name == event_name or event_name is None:
                if get_last:
                    last = recv

                    if not flush:
                        popped.append(recv)
                elif found is None:
                    found = recv
                elif not flush:
                    popped.append(recv)
            else:
                popped.append(recv)

        if not flush and get_last and last is not None:
            # remove the last item in the queue if we're returning it
            popped.pop()

        # put back any events that were skipped
        map(self._q.put_nowait, popped)

        return last if last is not None else found

    async def flush(self, event_name: str = None):
        """
        Flush the event queue

        :param event_name: The event name to filter (if any)
        """

        await self.poll(event_name=event_name, flush=True)


async def put_global(event: EventData):
    """
    Put an event in every connected session's event queue

    :param event: The event to replicate
    """

    for q in EventQueues.q:
        await q.put(event)
