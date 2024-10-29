# typing
from typing import Any

# stdlib
from unittest.async_case import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

# local
from xthulu.locks import _Locks, expire, get, hold, release


class TestLocks(IsolatedAsyncioTestCase):
    """Locks tests"""

    def setUp(self):
        _Locks.locks.clear()
        self._patch_cache = patch("xthulu.locks.cache", MagicMock())
        self.mock_cache = self._patch_cache.start()

    def tearDown(self):
        _Locks.locks.clear()
        self._patch_cache.stop()

    def test_get_lock(self):
        """Acquiring a new lock should populate the Locks singleton."""

        success = get("test_name", "test_lock")

        self.assertTrue(success, "Failed to acquire lock")
        self.assertIn("test_name", _Locks.locks, "Key not found")

    def test_get_lock_fails_if_exists(self):
        """Attempting to acquire an existing lock should fail."""

        self.mock_cache.lock.return_value = MagicMock()
        self.mock_cache.lock.return_value.acquire = MagicMock(
            return_value=False
        )

        success = get("test_name", "test_lock")

        self.assertFalse(success, "Failed to refuse getting an existing lock")
        self.assertNotIn("test_name", _Locks.locks, "Key should not exist")

    def test_hold_lock(self):
        """The `hold` context manager should acquire a lock successfully."""

        with hold("test_name", "test_lock") as l:
            self.assertTrue(l, "Failed to acquire lock")
            self.assertIn("test_name", _Locks.locks, "Key not found")

    def test_hold_lock_fails_if_exists(self):
        """Attempting to hold an existing lock should fail."""

        self.mock_cache.lock.return_value = MagicMock()
        self.mock_cache.lock.return_value.acquire = MagicMock(
            return_value=False
        )

        with hold("test_name", "test_lock") as l:
            self.assertFalse(l, "Failed to refuse holding existing lock")
            self.assertNotIn("test_name", _Locks.locks, "Key should not exist")

    def test_release_lock(self):
        """Releasing a lock should remove it from the singleton."""

        locks: dict[str, Any] = {"test_lock": MagicMock()}
        _Locks.locks["test_name"] = locks

        success = release("test_name", "test_lock")

        self.assertTrue(success, "Failed to release lock")
        self.assertNotIn("test_lock", locks, "Failed to remove key")

    def test_release_lock_removes_parent_when_empty(self):
        """Releasing a user's only lock should remove the parent object."""

        locks: dict[str, Any] = {"test_lock": MagicMock()}
        _Locks.locks["test_name"] = locks

        success = release("test_name", "test_lock")

        self.assertTrue(success, "Failed to release lock")
        self.assertNotIn("test_name", _Locks.locks)

    def test_expire_locks(self):
        """Expiring a user's locks should remove the parent object."""

        locks: dict[str, Any] = {
            "test_lock_1": MagicMock(),
            "test_lock_2": MagicMock(),
        }
        _Locks.locks["test_name"] = locks

        expire("test_name")

        self.assertNotIn("test_name", _Locks.locks)
