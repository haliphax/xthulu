"""SSH server CLI"""

# stdlib
from asyncio import get_event_loop
from signal import SIGTERM
import sys

# 3rd party
from asyncssh import Error as AsyncSSHError
from click import group

# local
from ..locks import _Locks, expire
from ..logger import log
from ..ssh import start_server


@group("ssh")
def cli():
    """SSH server commands"""


@cli.command()
def start():
    """Start SSH server process"""

    loop = get_event_loop()

    def shutdown():
        log.info("Shutting down")

        for owner in _Locks.locks.copy().keys():
            expire(owner)

        loop.stop()

    loop.add_signal_handler(SIGTERM, shutdown)

    try:
        loop.run_until_complete(start_server())
    except (OSError, AsyncSSHError) as exc:
        sys.exit(f"Error: {exc}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
