# typing
from typing import Any

# stdlib
from unittest.mock import patch, MagicMock

# 3rd party
import pytest

# local
from xthulu import locks
from xthulu.locks import _Locks


@pytest.fixture(autouse=True)
def mock_cache():
    with patch("xthulu.locks.cache", MagicMock()) as p:
        yield p


@pytest.fixture(autouse=True)
def clear_locks():
    _Locks.locks.clear()
    yield
    _Locks.locks.clear()


def test_get_lock():
    """Acquiring a new lock should populate the Locks singleton."""

    # act
    success = locks.get("test_name", "test_lock")

    # assert
    assert success
    assert "test_name" in _Locks.locks


def test_get_lock_fails_if_exists(mock_cache: MagicMock):
    """Attempting to acquire an existing lock should fail."""

    # arrange
    mock_cache.lock.return_value = MagicMock()
    mock_cache.lock.return_value.acquire = MagicMock(return_value=False)

    # act
    success = locks.get("test_name", "test_lock")

    # assert
    assert success is False
    assert "test_name" not in _Locks.locks


def test_hold_lock():
    """The `hold` context manager should acquire a lock successfully."""

    # act
    with locks.hold("test_name", "test_lock") as l:
        # assert
        assert l
        assert "test_name" in _Locks.locks


def test_hold_lock_fails_if_exists(mock_cache: MagicMock):
    """Attempting to hold an existing lock should fail."""

    # arrange
    mock_cache.lock.return_value = MagicMock()
    mock_cache.lock.return_value.acquire = MagicMock(return_value=False)

    # act
    with locks.hold("test_name", "test_lock") as l:
        # assert
        assert l is False
        assert "test_name" not in _Locks.locks


def test_release_lock():
    """Releasing a lock should remove it from the singleton."""

    # arrange
    locks_: dict[str, Any] = {"test_lock": MagicMock()}  # type: ignore
    _Locks.locks["test_name"] = locks_

    # act
    success = locks.release("test_name", "test_lock")

    # assert
    assert success
    assert "test_lock" not in locks_


def test_release_lock_removes_parent_when_empty():
    """Releasing a user's only lock should remove the parent object."""

    # arrange
    _Locks.locks["test_name"] = {"test_lock": MagicMock()}  # type: ignore

    # act
    success = locks.release("test_name", "test_lock")

    # assert
    assert success
    assert "test_name" not in _Locks.locks


def test_expire_locks():
    """Expiring a user's locks should remove the parent object."""

    # arrange
    _Locks.locks["test_name"] = {  # type: ignore
        "test_lock_1": MagicMock(),
        "test_lock_2": MagicMock(),
    }

    # act
    locks.expire("test_name")

    # assert
    assert "test_name" not in _Locks.locks
