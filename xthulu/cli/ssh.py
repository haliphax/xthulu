"""SSH server CLI"""

# stdlib
from asyncio import get_event_loop
from signal import SIGTERM
import sys

# 3rd party
from asyncssh import Error as AsyncSSHError, SSHAcceptor
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
    server: SSHAcceptor

    def shutdown():
        log.info("Shutting down")
        log.debug("Closing SSH listener")
        server.close()
        log.debug("Stopping event loop")
        loop.stop()
        log.debug("Expiring locks")

        for owner in _Locks.locks.copy().keys():
            log.debug(f"Expiring locks for {owner}")
            expire(owner)

    loop.add_signal_handler(SIGTERM, shutdown)

    try:
        server = loop.run_until_complete(start_server())
    except (OSError, AsyncSSHError) as exc:
        sys.exit(f"Error: {exc}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
