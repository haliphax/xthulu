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
"""Root blueprint"""


def create_app():
    """Create and configure the WSGI application."""

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
    print(app.routes)

    return app


def start_server():
    """Run web server via uvicorn server."""

    run(
        "xthulu.web.asgi:app",
        host=get_config("web.host"),
        port=int(get_config("web.port")),
        lifespan="off",
        limit_concurrency=1000,
        limit_max_requests=1000,
    )
