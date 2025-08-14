"""Event structs"""

# stdlib
from dataclasses import dataclass
from typing import Any


@dataclass
class EventData:
    """An event and its accompanying data"""

    name: str
    """The event namespace"""

    data: Any
    """The event's data payload"""
