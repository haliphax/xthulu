"""xthulu common structs"""

# stdlib
from collections import namedtuple

EventData = namedtuple(
    "EventData",
    (
        "name",
        "data",
    ),
)
"""Represents an event and its accompanying data."""

Script = namedtuple(
    "Script",
    (
        "name",
        "args",
        "kwargs",
    ),
)
"""Represents a userland Python script."""
