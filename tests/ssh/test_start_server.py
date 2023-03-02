"""SSH server startup tests"""

# type checking
from typing import Any

# stdlib
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

# 3rd party
from apiflask import APIFlask
from gino import Gino
from redis import Redis

# target
from xthulu.ssh import SSHServer, start_server
from xthulu.ssh.process_factory import handle_client

# local
from tests import run_coroutine
from tests.mocks.config import patch_get_config, test_config, test_ssh_config


class Resources:
    app = Mock(APIFlask)
    cache = Mock(Redis)
    config: dict[str, Any]
    db = Mock(Gino)


class TestStartServer(TestCase):

    """Test that the server starts up with the appropriate configuration."""

    def setUp(self):
        self._patch_resources = patch("xthulu.ssh.Resources", Resources)
        self.mock_resources = self._patch_resources.start()

        self._patch_listen = patch("xthulu.ssh.listen", AsyncMock())
        self.mock_listen = self._patch_listen.start()

    def tearDown(self):
        self._patch_resources.stop()
        self._patch_listen.stop()

    @patch("xthulu.ssh.get_config", patch_get_config(test_config))
    def test_db_bind(self):
        run_coroutine(start_server())

        self.mock_resources.db.set_bind.assert_awaited_once_with("test")

    @patch("xthulu.ssh.get_config", patch_get_config(test_config))
    def test_server_args(self):
        run_coroutine(start_server())

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
    def test_proxy_procotol(self, mock_listener: Mock):
        run_coroutine(start_server())

        mock_listener.assert_called_once()
        self.mock_listen.assert_awaited_once()
        assert "tunnel" in self.mock_listen.call_args[1]
