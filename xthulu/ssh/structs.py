"""SSH server structs"""

# stdlib
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class Script:

    """A userland Python script"""

    name: str
    """The script name, used for lookup"""

    args: Sequence[Any]
    """The script's `*args` list"""

    kwargs: dict[str, Any]
    """The scripts `**kwargs` dict"""
