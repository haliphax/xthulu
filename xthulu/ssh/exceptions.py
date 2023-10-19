"""SSH server exceptions"""

# local
from .structs import Script


class Goto(Exception):

    """Thrown to change the script without returning"""

    def __init__(self, script: str, *args, **kwargs):
        """
        Args:
            script: The script to run.
            args: The positional arguments to pass.
            kwargs: The keyword arguments to pass.
        """

        self.value = Script(script, args, kwargs)


class ProcessClosing(Exception):

    """Thrown when the `asyncssh.SSHServerProcess` is closing"""
