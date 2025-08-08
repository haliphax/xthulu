"""Web server tests"""

# stdlib
from unittest import TestCase
from unittest.mock import Mock, patch

# local
from tests.mocks.config import patch_get_config, test_config, test_web_config
from xthulu.web import create_app, start_server


@patch("xthulu.web.get_config", patch_get_config(test_config))
class TestStartWebServer(TestCase):
    """Web server tests"""

    def setUp(self):
        self._patch_import = patch("xthulu.web.import_module")
        self.mock_import: Mock = self._patch_import.start()

    def tearDown(self):
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
            lifespan="on",
        )

    @patch("xthulu.web.FastAPI.include_router")
    def test_includes_router(self, mock_include_router: Mock):
        """Server should include the API router."""

        # act
        create_app()

        # assert
        mock_include_router.assert_called()

    def test_imports_userland_modules(self):
        """Server should import userland modules."""

        # act
        create_app()

        # assert
        for mod in test_web_config["userland"]["modules"]:
            self.mock_import.assert_called_with(mod)
