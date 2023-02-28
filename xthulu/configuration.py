"""Configuration utilities"""

# type checking
from typing import Any

# local
from . import config


def get_config(path: str, default: Any = None) -> Any:
    """
    Get value from configuration path safely.

    Args:
        path: The configuration path to traverse for a value.
        default: The default value if the path does not exist.

    Returns:
        The configuration value or the provided default if the path does not
        exist.
    """

    store = config
    steps = path.split(".")

    for step in steps:
        store = store.get(step)

        if store is None:
            return default

    return store
