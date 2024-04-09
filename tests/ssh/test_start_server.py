"""SSH server startup tests"""

# type checking
from typing import Any

# stdlib
from logging import DEBUG, Logger
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, patch

# 3rd party
from fastapi import FastAPI
from gino import Gino
from redis import Redis

# local
from tests.mocks.config import patch_get_config, test_config, test_ssh_config
from xthulu.ssh import SSHServer, start_server
from xthulu.ssh.process_factory import handle_client


class Resources:
    app = Mock(FastAPI)
    cache = Mock(Redis)
    config: dict[str, Any]
    db = Mock(Gino)


class TestStartSSHServer(IsolatedAsyncioTestCase):
    """Test SSH server startup"""

    def setUp(self):
        self._patch_resources = patch("xthulu.ssh.Resources", Resources)
        self.mock_resources = self._patch_resources.start()

        self._patch_listen = patch("xthulu.ssh.listen", AsyncMock())
        self.mock_listen = self._patch_listen.start()

    def tearDown(self):
        self._patch_resources.stop()
        self._patch_listen.stop()

    @patch("xthulu.ssh.get_config", patch_get_config(test_config))
    async def test_db_bind(self):
        """Server should bind database connection during startup."""

        # act
        await start_server()

        # assert
        self.mock_resources.db.set_bind.assert_awaited_once_with(
            self.mock_resources.db.bind
        )

    @patch("xthulu.ssh.get_config", patch_get_config(test_config))
    async def test_server_args(self):
        """Server should bind SSH server to values from configuration."""

        # act
        await start_server()

        # assert
        ssh_config = test_config["ssh"]
        self.mock_listen.assert_awaited_once_with(
            **{
                "host": ssh_config["host"],
                "port": int(ssh_config["port"]),
                "server_factory": SSHServer,
                "server_host_keys": ssh_config["host_keys"],
                "process_factory": handle_client,
                "encoding": None,
            }
        )

    @patch(
        "xthulu.ssh.get_config",
        patch_get_config(
            {**test_config, "ssh": {**test_ssh_config, "proxy_protocol": True}}
        ),
    )
    @patch("xthulu.ssh.ProxyProtocolListener")
    async def test_proxy_procotol(self, mock_listener: Mock):
        """Server should use a PROXY tunnel if configured to do so."""

        # act
        await start_server()

        # assert
        mock_listener.assert_called_once()
        self.mock_listen.assert_awaited_once()
        assert "tunnel" in self.mock_listen.call_args[1]

    @patch("xthulu.ssh.get_config", patch_get_config(test_config))
    @patch("xthulu.ssh.start")
    async def test_trace_malloc_start(self, mock_start: Mock):
        """Server should call tracemalloc.start if debugging is enabled."""

        with patch.object(Logger, "getEffectiveLevel") as mock_level:
            # arrange
            mock_level.return_value = DEBUG

            # act
            await start_server()

            # assert
            mock_start.assert_called_once()
