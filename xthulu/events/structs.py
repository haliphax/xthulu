"""Event structs"""

# stdlib
from collections import namedtuple

EventData = namedtuple(
    "EventData",
    (
        "name",
        "data",
    ),
)
"""An event and its accompanying data"""
