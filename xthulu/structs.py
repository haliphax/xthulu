"xthulu common structs"

# stdlib
from collections import namedtuple

#: Represents an event and its accompanying data
EventData = namedtuple(
    "EventData",
    (
        "name",
        "data",
    ),
)
#: Represents a userland Python script
Script = namedtuple(
    "Script",
    (
        "name",
        "args",
        "kwargs",
    ),
)
