# type checking
from typing import Any

# stdlib
from unittest.mock import Mock

# 3rd party
from fastapi import FastAPI
from gino import Gino
from redis import Redis


class ResourcesMock:
    app = Mock(FastAPI)
    cache = Mock(Redis)
    config: dict[str, Any]
    db = Mock(Gino)
