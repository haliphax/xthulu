# api
from xthulu.events.structs import EventData
from xthulu.ssh.context import SSHContext


def handle_events(cx: SSHContext) -> tuple[list[EventData], bool]:
    """
    Handle common events. Will notify the userland script whether the screen
    is considered "dirty" based on the events retrieved.

    Args:
        cx: The context to inspect for events.

    Returns:
        The events (or an empty list) and whether or not the screen is "dirty".
    """

    events = []
    events += cx.events.get("resize")
    dirty = False

    for event in events:
        if event.name == "resize":
            dirty = True

    return events, dirty
