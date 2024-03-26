"""Event structs"""

# typing
from typing import Any

# stdlib
from dataclasses import dataclass


@dataclass
class EventData:
    """An event and its accompanying data"""

    name: str
    """The event namespace"""

    data: Any
    """The event's data payload"""
