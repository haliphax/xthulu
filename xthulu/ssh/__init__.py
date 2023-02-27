"SSH server module"

# type checking
from typing import Any

# 3rd party
from asyncssh import listen

# local
from .. import config, db, log
from .proxy_protocol import ProxyProtocolListener
from .server import SSHServer


async def start_server():
    """Run init tasks and throw SSH server into asyncio event loop"""

    await db.set_bind(config["db"]["bind"])
    ssh_config: dict[str, Any] = config["ssh"]
    host: str = ssh_config["host"]
    port = int(ssh_config["port"])
    log.info(f"SSH listening on {host}:{port}")

    kwargs = {
        "host": host,
        "port": port,
        "server_factory": SSHServer,
        "server_host_keys": config["ssh"]["host_keys"],
        "process_factory": SSHServer.handle_client,
        "encoding": None,
    }

    use_proxy: bool = ssh_config.get("proxy_protocol", False)

    if use_proxy:
        log.info("Using PROXY protocol v1 listener")
        kwargs["tunnel"] = ProxyProtocolListener()

    await listen(**kwargs)
