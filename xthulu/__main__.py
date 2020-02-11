"xthulu main entry point"

# stdlib
from asyncio import get_event_loop
import sys
# 3rd party
import asyncssh
# local
from . import log
from .ssh import start_server

loop = get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error: {}'.format(exc))

try:
    loop.run_forever()
except KeyboardInterrupt:
    log.info('Shutting down')
