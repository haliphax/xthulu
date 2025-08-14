"""Web server tests"""

# stdlib
from unittest.mock import Mock, patch

# 3rd party
import pytest

# local
from tests.mocks.config import patch_get_config, test_config, test_web_config
from xthulu.web import create_app, start_server


@pytest.fixture(autouse=True)
def mock_config():
    with patch("xthulu.web.get_config", patch_get_config(test_config)) as p:
        yield p


@pytest.fixture(autouse=True)
def mock_import_module():
    with patch("xthulu.web.import_module") as p:
        yield p


@patch("xthulu.web.run")
def test_uses_config(mock_run: Mock):
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
def test_includes_router(mock_include_router: Mock):
    """Server should include the API router."""

    # act
    create_app()

    # assert
    mock_include_router.assert_called()


def test_imports_userland_modules(mock_import_module: Mock):
    """Server should import userland modules."""

    # act
    create_app()

    # assert
    for mod in test_web_config["userland"]["modules"]:  # type: ignore
        mock_import_module.assert_called_with(mod)
