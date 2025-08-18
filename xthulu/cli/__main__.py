"""Command line entrypoint"""

# stdlib
from asyncio import new_event_loop, set_event_loop_policy

# 3rd party
from uvloop import EventLoopPolicy

# local
from . import cli


set_event_loop_policy(EventLoopPolicy())
loop = new_event_loop()

try:
    cli()
finally:
    loop.close()
