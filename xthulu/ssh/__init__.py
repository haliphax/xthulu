"""SSH server module"""

# type checking
from typing import Any

# stdlib
from tracemalloc import start

# 3rd party
from asyncssh import listen

# local
from ..configuration import get_config
from ..logger import log
from ..resources import Resources
from .codecs import register_encodings
from .process_factory import handle_client
from .proxy_protocol import ProxyProtocolListener
from .server import SSHServer


async def start_server():
    """Run init tasks and throw SSH server into asyncio event loop."""

    register_encodings()
    res = Resources()
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

    await res.db.set_bind(get_config("db.bind"))

    try:
        await listen(**kwargs)
    finally:
        await res.db.pop_bind().close()
