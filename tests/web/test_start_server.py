"""Web server tests"""

# type checking
from typing import Any

# stdlib
from unittest import TestCase
from unittest.mock import Mock, patch

# 3rd party
from fastapi import FastAPI
from gino import Gino
from redis import Redis

# local
from tests.mocks.config import patch_get_config, test_config, test_web_config
from xthulu.web import create_app, start_server


class Resources:
    app = Mock(FastAPI)
    cache = Mock(Redis)
    config: dict[str, Any]
    db = Mock(Gino)


@patch("xthulu.web.get_config", patch_get_config(test_config))
class TestStartWebServer(TestCase):
    """Web server tests"""

    def setUp(self):
        self._patch_resources = patch("xthulu.web.Resources", Resources)
        self.mock_resources = self._patch_resources.start()

        self._patch_import = patch("xthulu.web.import_module")
        self.mock_import: Mock = self._patch_import.start()

    def tearDown(self):
        self._patch_resources.stop()
        self._patch_import.stop()

    @patch("xthulu.web.run")
    def test_uses_config(self, mock_run: Mock):
        """Server should bind listener using loaded configuration."""

        # act
        start_server()

        # assert
        mock_run.assert_called_once_with(
            "xthulu.web.asgi:app",
            host=test_web_config["host"],
            port=test_web_config["port"],
            lifespan="off",
        )

    def test_includes_router(self):
        """Server should include the API router."""

        # act
        create_app()

        # assert
        self.mock_resources.app.include_router.assert_called()

    def test_imports_userland_modules(self):
        """Server should import userland modules."""

        # act
        create_app()

        # assert
        for mod in test_web_config["userland"]["modules"]:
            self.mock_import.assert_called_with(mod)
