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
"""An event and its accompanying data"""

Script = namedtuple(
    "Script",
    (
        "name",
        "args",
        "kwargs",
    ),
)
"""A userland Python script"""
