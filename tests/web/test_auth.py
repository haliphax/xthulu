"""Authentication tests"""

# stdlib
from unittest.mock import AsyncMock, Mock, patch

# 3rd party
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
import pytest

# local
from xthulu.models.user import User
from xthulu.web.auth import login_user


@pytest.fixture(autouse=True)
def mock_depends():
    with patch("xthulu.web.auth.Depends") as p:
        yield p


@pytest.fixture
def mock_session():
    with patch("xthulu.web.auth.db_session") as p:
        yield p.return_value.__aenter__.return_value


@pytest.mark.asyncio
@patch("xthulu.web.auth.get_config")
async def test_guest_login(mock_config: Mock, mock_session: Mock):
    """Login should succeed with no password for special cases."""

    # arrange
    mock_user = Mock()
    mock_user.name = "test"
    mock_user.password, mock_user.salt = User.hash_password("test")
    mock_config.return_value = ["test"]
    mock_session.exec = AsyncMock()
    mock_session.exec.return_value.one_or_none = Mock(return_value=mock_user)

    # act
    result = await login_user(
        HTTPBasicCredentials(username="test", password="")
    )

    # assert
    assert result == mock_user


@pytest.mark.asyncio
async def test_password_login(mock_session: Mock):
    """Login should succeed with a known username and password."""

    # arrange
    mock_user = Mock()
    mock_user.password, mock_user.salt = User.hash_password("test")
    mock_session.exec = AsyncMock()
    mock_session.exec.return_value.one_or_none = Mock(return_value=mock_user)

    # act
    result = await login_user(
        HTTPBasicCredentials(username="test", password="test")
    )

    # assert
    assert result == mock_user


@pytest.mark.asyncio
async def test_bad_username(mock_session: Mock):
    """Login should fail with an unknown username."""

    # arrange
    mock_session.exec = AsyncMock()
    mock_session.exec.return_value.one_or_none = Mock(return_value=None)

    # act
    try:
        await login_user(HTTPBasicCredentials(username="test", password="test"))

        # assert
        assert False
    except HTTPException as ex:
        assert ex.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_bad_password(mock_session: Mock):
    """Login should fail with an incorrect password."""

    # arrange
    mock_user = Mock()
    mock_user.password, mock_user.salt = User.hash_password("test")
    mock_session.exec = AsyncMock()
    mock_session.exec.return_value.one_or_none = Mock(return_value=mock_user)

    # act
    try:
        await login_user(HTTPBasicCredentials(username="test", password="bad"))

        # assert
        assert False
    except HTTPException as ex:
        assert ex.status_code == status.HTTP_401_UNAUTHORIZED
