"""SSH server startup tests"""

# stdlib
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

# target
from xthulu.ssh import start_server
from xthulu.ssh.server import SSHServer
from xthulu.ssh.process_factory import handle_client

# local
from tests import run_coroutine


class TestStartServer(TestCase):

    """Test that the server starts up with the appropriate configuration."""

    test_ssh_config = {
        "host": "0.0.0.0",
        "host_keys": "/test",
        "port": "8022",
    }
    """Default SSH configuration for testing"""

    test_config = {"db": {"bind": "test"}, "ssh": test_ssh_config}
    """Default overall configuration for testing"""

    def setUp(self):
        self._patch_db = patch("xthulu.ssh.db")
        self.mock_db = self._patch_db.start()

        self._patch_listen = patch("xthulu.ssh.listen", AsyncMock())
        self.mock_listen = self._patch_listen.start()

    def tearDown(self):
        self._patch_db.stop()
        self._patch_listen.stop()

    @patch("xthulu.config", test_config)
    def test_db_bind(self):
        run_coroutine(start_server())

        set_bind: AsyncMock = self.mock_db.set_bind
        set_bind.assert_awaited_once_with("test")

    @patch("xthulu.config", test_config)
    def test_server_args(self):
        run_coroutine(start_server())

        ssh_config = self.test_config["ssh"]
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
        "xthulu.config",
        {
            **test_config,
            "ssh": {**test_ssh_config, "proxy_protocol": True},
        },
    )
    @patch("xthulu.ssh.ProxyProtocolListener")
    def test_proxy_procotol(self, mock_listener: Mock):
        run_coroutine(start_server())

        mock_listener.assert_called_once()
        self.mock_listen.assert_awaited_once()
        assert "tunnel" in self.mock_listen.call_args[1]
