"""Web server tests"""

# type checking
from typing import Any

# stdlib
from unittest import TestCase
from unittest.mock import Mock, patch

# 3rd party
from apiflask import APIFlask
from gino import Gino
from redis import Redis

# local
from tests.mocks.config import patch_get_config, test_config, test_web_config
from xthulu.web import start_server
from xthulu.web.asgi import main


class Resources:
    app = Mock(APIFlask)
    cache = Mock(Redis)
    config: dict[str, Any]
    db = Mock(Gino)


@patch("xthulu.web.get_config", patch_get_config(test_config))
class TestStartWebServer(TestCase):

    """Web server tests"""

    def setUp(self):
        self._patch_resources = patch("xthulu.web.Resources", Resources)
        self.mock_resources = self._patch_resources.start()

        self._patch_run = patch("xthulu.web.run")
        self.mock_run = self._patch_run.start()

    def tearDown(self):
        self._patch_resources.stop()
        self._patch_run.stop()

    def test_uses_config(self):
        """Server should bind using loaded configuration."""

        start_server()

        self.mock_run.assert_called_once_with(
            "xthulu.web.asgi:asgi_app",
            host=test_web_config["host"],
            port=test_web_config["port"],
        )

    def test_db_bind(self):
        """Server should bind database connection during startup."""

        start_server()

        self.mock_resources.db.set_bind.assert_awaited_once_with("test")

    @patch("xthulu.web.api")
    @patch("xthulu.web.app")
    def test_registers_blueprint(self, mock_app: Mock, mock_api: Mock):
        """ASGI entrypoint should register the API blueprint."""

        main()

        mock_app.register_blueprint.assert_called_once_with(mock_api)
