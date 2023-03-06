"""Reusable mock configuration dicts"""

# type checking
from typing import Any

# local
from xthulu.configuration import get_config

test_ssh_config = {
    "host": "1.2.3.4",
    "host_keys": "/test",
    "port": 9999,
}
"""Default SSH configuration for testing"""

test_web_config = {
    "host": "1.2.3.4",
    "port": 9999,
    "userland": {"paths": "/test"},
}
"""Default web server configuration for testing"""

test_config = {
    "cache": {"host": "test", "port": 9999},
    "db": {"bind": "test"},
    "ssh": test_ssh_config,
    "web": test_web_config,
}
"""Default overall configuration for testing"""


def patch_get_config(config: dict[str, Any]):
    """
    Used for patching the `get_config` method.

    Args:
        config: The configuration dictionary to use in place of the default.
    """

    def wrapped(
        path: str,
        default: Any = None,
        config: dict[str, Any] | None = config,
    ):
        return get_config(path, default, config)

    return wrapped
