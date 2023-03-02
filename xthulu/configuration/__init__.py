"""Configuration utilities"""

# type checking
from typing import Any, Mapping


def deep_update(source: dict, overrides: Mapping):
    """
    Update a nested dictionary in place.
    """

    for key, value in overrides.items():
        if isinstance(value, Mapping) and value:
            returned = deep_update(source.get(key, {}), value)
            source[key] = returned
        else:
            source[key] = overrides[key]

    return source


def get_config(
    path: str, default: Any = None, config: dict[str, Any] | None = None
) -> Any:
    """
    Get value from configuration path safely.

    Args:
        path: The configuration path to traverse for a value.
        default: The default value if the path does not exist.
        config: The configuration dictionary to scan.
            If this is not provided, the system configuration will be loaded
            by default.

    Returns:
        The configuration value or the provided default if the path does not
        exist.
    """

    store = config

    if store is None:
        from ..resources import Resources

        store = Resources().config

    steps = path.split(".")

    for step in steps:
        store = store.get(step)

        if store is None:
            return default

    return store
