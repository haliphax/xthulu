"""xthulu exceptions module"""

from .structs import Script


class Goto(Exception):

    """Thrown to change the script without returning"""

    def __init__(self, script: str, *args, **kwargs):
        """
        Thrown to change the script without returning.

        Args:
            script: The script to run.
        """

        self.value = Script(script, args, kwargs)


class ProcessClosing(Exception):

    """Thrown when the SSHServerProcess is closing"""
