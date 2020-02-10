# stdlib
import asyncio as aio
import sys
# 3rd party
import asyncssh
# local
from . import start_server

loop = aio.get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error: %s' % str(exc))

loop.run_forever()
