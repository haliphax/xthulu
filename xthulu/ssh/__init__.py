"""SSH server module"""

# type checking
from typing import Any

# stdlib
from tracemalloc import start

# 3rd party
from asyncssh import listen

# local
from .. import bind_redis, db


async def start_server():
    """Run init tasks and throw SSH server into asyncio event loop."""

    # bind redis before importing anything to do with shared locks
    bind_redis()

    from ..configuration import get_config
    from ..logger import log
    from .encodings import register_encodings
    from .process_factory import handle_client
    from .proxy_protocol import ProxyProtocolListener
    from .server import SSHServer

    register_encodings()
    await db.set_bind(get_config("db.bind"))
    ssh_config: dict[str, Any] = get_config("ssh")
    host: str = ssh_config["host"]
    port = int(ssh_config["port"])
    log.info(f"SSH listening on {host}:{port}")

    kwargs = {
        "host": host,
        "port": port,
        "server_factory": SSHServer,
        "server_host_keys": ssh_config["host_keys"],
        "process_factory": handle_client,
        "encoding": None,
    }

    use_proxy: bool = get_config("ssh.proxy_protocol", False)

    if use_proxy:
        log.info("Using PROXY protocol v1 listener")
        kwargs["tunnel"] = ProxyProtocolListener()

    if bool(get_config("debug.enabled", False)):
        start()

    await listen(**kwargs)
