"""Resources tests"""

# type checking
from typing import Type

# stdlib
from unittest.mock import Mock, patch

# 3rd party
import pytest
from redis import Redis
from sqlalchemy.ext.asyncio.engine import AsyncEngine

# local
from xthulu.configuration.default import default_config
from xthulu.resources import db_session, Resources


@pytest.fixture(autouse=True)
def reset_singleton():
    if hasattr(Resources, "_singleton"):
        del Resources._singleton

    yield

    if hasattr(Resources, "_singleton"):
        del Resources._singleton


@pytest.fixture(autouse=True)
def mock_exists():
    with patch("xthulu.resources.exists") as p:
        p.return_value = True
        yield p


@patch("xthulu.resources.load")
def test_config_file_loaded(mock_load: Mock):
    """Constructor should load the configuration file."""

    # act
    Resources()

    # assert
    mock_load.assert_called_once_with("data/config.toml")


@patch("xthulu.resources.exists", return_value=False)
def test_config_fall_back(*_):
    """Constructor should use default config if file isn't found."""

    # act
    res = Resources()

    # assert
    assert res.config == default_config


@patch("xthulu.resources.environ", Mock(get=lambda *_: "test"))
@patch("xthulu.resources.load")
def test_config_file_from_env_used(mock_load: Mock):
    """Constructor should use the filename from environ if available."""

    # act
    Resources()

    # assert
    mock_load.assert_called_once_with("test")


@pytest.mark.parametrize(
    ["name", "cls"], [["cache", Redis], ["db", AsyncEngine]]
)
@patch("xthulu.resources.load", lambda *_: {})
def test_property_assignment(name: str, cls: Type):
    """Constructor should assign properties to singleton appropriately."""

    # act
    resources = Resources()

    # assert
    assert isinstance(getattr(resources, name), cls)


@pytest.mark.asyncio
@patch("xthulu.resources.AsyncSession")
@patch("xthulu.resources.Resources")
async def test_db_session(mock_resources: Mock, mock_session: Mock):
    """The `db_session` function should wrap the Resources.db engine."""

    res = Mock()
    mock_resources.return_value = res

    # act
    async with db_session():
        pass

    # assert
    mock_session.assert_called_once_with(res.db)
