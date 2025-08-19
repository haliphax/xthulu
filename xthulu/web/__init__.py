"""Web server module"""

# stdlib
from contextlib import asynccontextmanager
from importlib import import_module
from logging import getLogger
from logging.handlers import TimedRotatingFileHandler
from os import path

# 3rd party
from fastapi import APIRouter, FastAPI
from uvicorn import run

# local
from ..configuration import get_config
from ..logger import log, namer, rotator

api = APIRouter()
"""Main router"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan; handles startup and shutdown."""

    access_log = getLogger("uvicorn.access")
    fileHandler = TimedRotatingFileHandler(
        path.join("run", "logs", "www.log"), when="d"
    )
    fileHandler.rotator = rotator
    fileHandler.namer = namer
    access_log.addHandler(fileHandler)
    yield


def create_app():
    """Create and configure the ASGI application."""

    app = FastAPI(lifespan=lifespan)

    for mod in list(get_config("web.userland.modules", [])):
        m = import_module(mod)
        mod_api = getattr(m, "api")

        if not mod_api:  # pragma: no cover
            log.warning(f"No APIRouter found in userland web module {mod}")
            continue

        app.include_router(mod_api, prefix="/api")

    app.include_router(api, prefix="/api")

    return app


def start_server():
    """Run ASGI web application in a uvicorn server."""

    run(
        "xthulu.web.asgi:app",
        host=get_config("web.host"),
        port=int(get_config("web.port")),
        lifespan="on",
    )
