"""SSH server startup tests"""

# stdlib
from logging import DEBUG, Logger
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

# 3rd party
import pytest

# local
from tests.mocks.config import patch_get_config, test_config, test_ssh_config
from xthulu.ssh import SSHServer, start_server
from xthulu.ssh.process_factory import handle_client


@pytest.fixture(autouse=True)
def mock_config():
    with patch("xthulu.ssh.get_config", patch_get_config(test_config)) as p:
        yield p


@pytest.fixture(autouse=True)
def mock_listen():
    with patch("xthulu.ssh.listen", AsyncMock()) as p:
        yield p


@pytest.mark.asyncio
async def test_server_args(mock_listen: Mock):
    """Server should bind SSH server to values from configuration."""

    # act
    await start_server()

    # assert
    ssh_config: dict[str, Any] = test_config["ssh"]  # type: ignore
    mock_listen.assert_awaited_once_with(
        **{
            "host": ssh_config["host"],
            "port": int(ssh_config["port"]),
            "server_factory": SSHServer,
            "server_host_keys": ssh_config["host_keys"],
            "process_factory": handle_client,
            "encoding": None,
        }
    )


@pytest.mark.asyncio
@patch(
    "xthulu.ssh.get_config",
    patch_get_config(
        {**test_config, "ssh": {**test_ssh_config, "proxy_protocol": True}}
    ),
)
@patch("xthulu.ssh.ProxyProtocolListener")
async def test_proxy_procotol(mock_listener: Mock, mock_listen: Mock):
    """Server should use a PROXY tunnel if configured to do so."""

    # act
    await start_server()

    # assert
    mock_listener.assert_called_once()
    mock_listen.assert_awaited_once()
    assert "tunnel" in mock_listen.call_args[1]


@pytest.mark.asyncio
@patch("xthulu.ssh.start")
async def test_trace_malloc_start(mock_start: Mock):
    """Server should call tracemalloc.start if debugging is enabled."""

    # arrange
    with patch.object(Logger, "getEffectiveLevel", return_value=DEBUG):
        # act
        await start_server()

        # assert
        mock_start.assert_called_once()
