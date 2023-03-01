"""xthulu module initialization"""

# type checking
from typing import Any

# stdlib
from os import environ
from os.path import exists, join
from sys import stderr

# 3rd party
from gino import Gino
from redis import Redis
from toml import load

# local
from .configuration import deep_update, get_config
from .configuration.default import default_config

config: dict[str, Any] = default_config.copy()
"""xthulu configuration"""

config_file = (
    environ["XTHULU_CONFIG"]
    if "XTHULU_CONFIG" in environ
    else join("data", "config.toml")
)
"""xthulu configuration file"""

if exists(config_file):
    deep_update(config, load(config_file))
    print(f"Loaded configuration file: {config_file}", file=stderr)
else:
    print(f"Configuration file not found: {config_file}", file=stderr)

db = Gino()
"""Gino database API instance"""

cache: Redis
"""Redis cache connection"""


def bind_redis():
    global cache
    cache = Redis(
        host=get_config("cache.host"), port=int(get_config("cache.port"))
    )


__all__ = (
    "bind_redis",
    "cache",
    "config",
    "config_file",
    "db",
)

if __name__ == "__main__":
    bind_redis()
