"""Shared resource singleton"""

# stdlib
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Any
from os import environ
from os.path import exists, join

# 3rd party
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from toml import load  # type: ignore

# local
from .configuration import deep_update, get_config
from .configuration.default import default_config

log = getLogger(__name__)


class Resources:
    """Shared system resources"""

    cache: Redis
    """Redis connection"""

    config: dict[str, Any]
    """System configuration"""

    config_file: str
    """Configuration file path"""

    db: AsyncEngine
    """Database engine"""

    def __new__(cls):
        if hasattr(cls, "_singleton"):
            return cls._singleton

        singleton = super().__new__(cls)
        singleton._load_config()
        singleton.cache = Redis(
            host=singleton._config("cache.host"),
            port=int(singleton._config("cache.port")),
            db=int(singleton._config("cache.db")),
        )
        singleton.db = create_async_engine(
            singleton._config("db.bind"), future=True
        )
        cls._singleton = singleton

        return cls._singleton

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
            log.warning(f"Configuration file not found: {self.config_file}")


@asynccontextmanager
async def db_session():
    """Get a `sqlmodel.ext.asyncio.session.AsyncSession` object."""

    async with AsyncSession(Resources().db) as session:
        yield session
