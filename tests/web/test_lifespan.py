"""Lifespan tests"""

# stdlib
from unittest.mock import Mock, patch

# 3rd party
import pytest

# local
from xthulu.web import lifespan


@pytest.mark.asyncio
@patch("xthulu.web.getLogger")
async def test_lifespan(mock_get_logger: Mock):
    """Lifespan method should add a logging handler."""

    # act
    async with lifespan(Mock()):
        pass

    # assert
    mock_get_logger.return_value.addHandler.assert_called_once()
