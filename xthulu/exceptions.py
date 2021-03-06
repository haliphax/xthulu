"xthulu exceptions module"

from .structs import Script


class Goto(Exception):

    "Thrown to change script without returning"

    def __init__(self, script, *args, **kwargs):
        self.value = Script(script, args, kwargs)


class ProcessClosing(Exception):

    "Thrown when the SSHServerProcess is closing"
