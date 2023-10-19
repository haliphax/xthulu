"""Web server module"""

# stdlib
from importlib import import_module

# 3rd party
from fastapi import APIRouter
from uvicorn import run

# local
from ..configuration import get_config
from ..logger import log
from ..resources import Resources

api = APIRouter()
"""Main router"""


def create_app():
    """Create and configure the ASGI application."""

    res = Resources()
    app = res.app
    import_module(".routes", __name__)

    for mod in list(get_config("web.userland.modules", [])):
        m = import_module(mod)
        mod_api = getattr(m, "api")

        if not mod_api:
            log.warn(f"No APIRouter found in userland web module {mod}")
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
        lifespan="off",
    )
