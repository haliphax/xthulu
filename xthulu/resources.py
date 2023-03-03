"""Shared resource singleton"""

# type checking
from typing import Any

# stdlib
from logging import getLogger
from os import environ
from os.path import exists, join

# 3rd party
from apiflask import APIFlask
from gino import Gino
from redis import Redis
from toml import load

# local
from .configuration import deep_update, get_config
from .configuration.default import default_config

log = getLogger(__name__)


class Resources:

    """Shared system resources"""

    app: APIFlask
    """Web application"""

    cache: Redis
    """Redis connection"""

    config: dict[str, Any]
    """System configuration"""

    config_file: str
    """Configuration file path"""

    db: Gino
    """Database connection"""

    def __new__(cls):
        if hasattr(cls, "_singleton"):
            return cls._singleton

        self = super().__new__(cls)
        self._load_config()
        self.app = APIFlask(__name__)
        self.cache = Redis(
            host=self._config("cache.host"),
            port=int(self._config("cache.port")),
            db=int(self._config("cache.db")),
        )
        self.db = Gino(bind=self._config("db.bind"))
        cls._singleton = self

        return self

    def _config(self, path: str, default: Any = None):
        return get_config(path, default, self.config)

    def _load_config(self):
        self.config = default_config.copy()
        self.config_file = environ.get(
            "XTHULU_CONFIG", join("data", "config.toml")
        )

        if exists(self.config_file):
            deep_update(self.config, load(self.config_file))
            log.info(f"Loaded configuration file: {self.config_file}")
        else:
            log.warn(f"Configuration file not found: {self.config_file}")
