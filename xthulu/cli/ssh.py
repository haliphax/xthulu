"""SSH server CLI"""

# stdlib
from signal import SIGTERM
import sys

# 3rd party
from asyncssh import Error as AsyncSSHError, SSHAcceptor
from click import group

# local
from ._util import loop
from ..locks import _Locks, expire
from ..logger import log
from ..ssh import start_server


@group("ssh")
def cli():
    """SSH server commands"""


@cli.command()
def start():
    """Start SSH server process"""

    _loop = loop()
    server: SSHAcceptor  # type: ignore

    def shutdown():
        log.info("Shutting down")
        log.debug("Closing SSH listener")
        server.close()
        log.debug("Stopping event loop")
        _loop.stop()
        log.debug("Expiring locks")

        for owner in _Locks.locks.copy().keys():
            log.debug(f"Expiring locks for {owner}")
            expire(owner)

    _loop.add_signal_handler(SIGTERM, shutdown)

    try:
        server = _loop.run_until_complete(start_server())
    except (OSError, AsyncSSHError) as exc:  # pragma: no cover
        sys.exit(f"Error: {exc}")

    try:
        _loop.run_forever()
    except KeyboardInterrupt:
        pass
