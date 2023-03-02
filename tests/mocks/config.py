"""Reusable mock configuration dicts"""

# type checking
from typing import Any

# target
from xthulu.configuration import get_config

test_ssh_config = {
    "host": "0.0.0.0",
    "host_keys": "/test",
    "port": "8022",
}
"""Default SSH configuration for testing"""

test_config = {
    "cache": {"host": "test", "port": 1234},
    "db": {"bind": "test"},
    "ssh": test_ssh_config,
}
"""Default overall configuration for testing"""


def patch_get_config(config: dict[str, Any]):
    """
    Used for patching the `get_config` method. The returned decorator takes a
    mocked configuration dict as its only argument.
    """

    def wrapped(
        path: str,
        default: Any = None,
        config: dict[str, Any] | None = config,
    ):
        return get_config(path, default, config)

    return wrapped
