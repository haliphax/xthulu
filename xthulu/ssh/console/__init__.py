"""An SSH-integrated Console for use with rich/Textual"""

# stdlib
from typing import Any, Literal, Mapping

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
        color_term = _environ.get("COLORTERM") if _environ else None
        term_type = (_environ.get("TERM") if _environ else None) or ""
        color_system: (
            Literal["auto", "standard", "256", "truecolor", "windows"] | None
        ) = (
            "truecolor"
            if color_term == "truecolor" or term_type.find("truecolor") >= 0
            else "256"
            if term_type.find("256") >= 0
            else "standard"
        )
        super(XthuluConsole, self).__init__(
            **kwargs,
            color_system=color_system,
            file=FileWrapper(ssh_writer, encoding),  # type: ignore
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
