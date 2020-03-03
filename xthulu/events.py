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

    async def poll(self, event_name):
        "Check for specific event"

        popped = []
        found = None

        while not self._q.empty() and found is None:
            recv = await self._q.get()

            if recv.name == event_name:
                found = recv
            else:
                popped.append(recv)

        # put back any events that were skipped
        for ev in popped:
            await self._q.put(ev)

        return found
