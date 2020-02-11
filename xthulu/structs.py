"xthulu common structs"

# stdlib
from collections import namedtuple

EventData = namedtuple('EventData', ('name', 'data',))
Script = namedtuple('Script', ('name', 'args', 'kwargs',))
