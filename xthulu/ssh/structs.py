"""SSH server structs"""

# stdlib
from collections import namedtuple

Script = namedtuple(
    "Script",
    (
        "name",
        "args",
        "kwargs",
    ),
)
"""A userland Python script"""
