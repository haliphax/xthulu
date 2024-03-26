"""An SSH-integrated Console for use with rich/Textual"""

# typing
from typing import Any, Mapping

# 3rd party
from asyncssh import SSHWriter
from rich.console import Console

# local
from .internal.file_wrapper import FileWrapper


class XthuluConsole(Console):
    """
    Wrapper around rich's Console for integrating with
    `xthulu.ssh.context.SSHContext` queues
    """

    _encoding: str

    def __init__(
        self,
        *,
        encoding: str,
        height: int | None = None,
        ssh_writer: SSHWriter[Any],
        width: int | None = None,
        _environ: Mapping[str, str] | None = None,
        **kwargs,
    ):
        self.encoding = encoding
        super().__init__(
            **kwargs,
            file=FileWrapper(ssh_writer, encoding),
            force_interactive=True,
            force_terminal=True,
            highlight=False,
            width=width,
            height=height,
            _environ=_environ,
        )

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, val: str):
        self._encoding = val
