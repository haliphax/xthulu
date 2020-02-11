"xthulu exceptions module"

from .structs import EventData, Script


class Goto(Exception):

    "Thrown to change script without returning"

    def __init__(self, script, *args, **kwargs):
        self.value = Script(name=script, args=args, kwargs=kwargs)


class ProcessClosingException(Exception):

    "Thrown when the SSHServerProcess is closing"

    pass


class Event(Exception):

    "Thrown when a server event takes place"

    def __init__(self, event, data):
        self.value = EventData(name=event, data=data)
