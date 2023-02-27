"""Configuration tests"""

# stdlib
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

# target
from xthulu.ssh import start_server
from xthulu.ssh.server import SSHServer

# local
from tests import run_coroutine


class TestConfiguration(TestCase):
    default_config = {
        "db": {
            "bind": "test",
        },
        "ssh": {
            "host": "0.0.0.0",
            "host_keys": "/test",
            "port": "8022",
        },
    }
    """Default configuration for testing"""

    def setUp(self):
        self._patch_db = patch("xthulu.ssh.db")
        self.mock_db = self._patch_db.start()

        self._patch_listen = patch("xthulu.ssh.listen", AsyncMock())
        self.mock_listen = self._patch_listen.start()

    def tearDown(self):
        self._patch_db.stop()
        self._patch_listen.stop()

    @patch("xthulu.ssh.config", default_config)
    def test_db_bind(self):
        run_coroutine(start_server())

        set_bind: AsyncMock = self.mock_db.set_bind
        set_bind.assert_awaited_once_with("test")

    @patch("xthulu.ssh.config", default_config)
    def test_server_args(self):
        config = self.default_config
        ssh_config = config["ssh"]

        run_coroutine(start_server())

        self.mock_listen.assert_awaited_once_with(
            **{
                "host": ssh_config["host"],
                "port": int(ssh_config["port"]),
                "server_factory": SSHServer,
                "server_host_keys": ssh_config["host_keys"],
                "process_factory": SSHServer.handle_client,
                "encoding": None,
            }
        )

    @patch(
        "xthulu.ssh.config",
        {
            **default_config,
            **{
                "ssh": {
                    "host": "0.0.0.0",
                    "host_keys": "/test",
                    "port": 8022,
                    "proxy_protocol": True,
                }
            },
        },
    )
    @patch("xthulu.ssh.ProxyProtocolListener")
    def test_proxy_procotol(self, mock_listener: Mock):
        run_coroutine(start_server())

        mock_listener.assert_called_once()
        self.mock_listen.assert_awaited_once()
        assert "tunnel" in self.mock_listen.call_args[1]
