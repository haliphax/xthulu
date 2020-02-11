"xthulu exceptions module"


class Goto(Exception):

    "Thrown to change script without returning"

    def __init__(self, script, *args, **kwargs):
        self.value = Script(name=script, args=args, kwargs=kwargs)


class ProcessClosingException(Exception):

    "Thrown when the SSHServerProcess is closing"

    pass
