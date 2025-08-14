# typing
from typing import Any

# stdlib
from unittest.mock import patch, MagicMock

# 3rd party
import pytest

# local
from xthulu.locks import _Locks, expire, get, hold, release


@pytest.fixture(autouse=True)
def mock_cache():
    with patch("xthulu.locks.cache", MagicMock()) as p:
        yield p

    _Locks.locks.clear()


def test_get_lock():
    """Acquiring a new lock should populate the Locks singleton."""

    success = get("test_name", "test_lock")

    assert success
    assert "test_name" in _Locks.locks


def test_get_lock_fails_if_exists(mock_cache: MagicMock):
    """Attempting to acquire an existing lock should fail."""

    mock_cache.lock.return_value = MagicMock()
    mock_cache.lock.return_value.acquire = MagicMock(return_value=False)

    success = get("test_name", "test_lock")

    assert success is False
    assert "test_name" not in _Locks.locks


def test_hold_lock():
    """The `hold` context manager should acquire a lock successfully."""

    with hold("test_name", "test_lock") as l:
        assert l
        assert "test_name" in _Locks.locks


def test_hold_lock_fails_if_exists(mock_cache: MagicMock):
    """Attempting to hold an existing lock should fail."""

    mock_cache.lock.return_value = MagicMock()
    mock_cache.lock.return_value.acquire = MagicMock(return_value=False)

    with hold("test_name", "test_lock") as l:
        assert l is False
        assert "test_name" not in _Locks.locks


def test_release_lock():
    """Releasing a lock should remove it from the singleton."""

    locks: dict[str, Any] = {"test_lock": MagicMock()}  # type: ignore
    _Locks.locks["test_name"] = locks

    success = release("test_name", "test_lock")

    assert success
    assert "test_lock" not in locks


def test_release_lock_removes_parent_when_empty():
    """Releasing a user's only lock should remove the parent object."""

    locks: dict[str, Any] = {"test_lock": MagicMock()}  # type: ignore
    _Locks.locks["test_name"] = locks

    success = release("test_name", "test_lock")

    assert success
    assert "test_name" not in _Locks.locks


def test_expire_locks():
    """Expiring a user's locks should remove the parent object."""

    locks: dict[str, Any] = {  # type: ignore
        "test_lock_1": MagicMock(),
        "test_lock_2": MagicMock(),
    }
    _Locks.locks["test_name"] = locks

    expire("test_name")

    assert "test_name" not in _Locks.locks
