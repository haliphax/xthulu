"""Web server module"""

# stdlib
from asyncio import get_event_loop
from importlib import import_module

# 3rd party
from apiflask import APIBlueprint
from uvicorn import run

# local
from ..resources import Resources
from ..configuration import get_config
from ..logger import log

api = APIBlueprint("api", __name__, url_prefix="/api")
"""Root blueprint"""


@api.route("/")
def index():
    """Demonstration index route."""

    return {"xthulu": True}


def create_app():
    """Create and configure the WSGI application."""

    res = Resources()
    app = res.app
    get_event_loop().create_task(res.db.set_bind(get_config("db.bind")))

    for mod in list(get_config("web.userland.modules", [])):
        loaded = import_module(mod)

        if hasattr(loaded, "api"):
            log.info(f"Loading userland web module: {mod}")
            mod_api: APIBlueprint = getattr(loaded, "api")
            api.register_blueprint(mod_api)
        else:
            log.warn(f"No api object found for userland web module: {mod}")

    app.register_blueprint(api)

    return app


def start_server():
    """Run web server via uvicorn server."""

    run(
        "xthulu.web.asgi:asgi_app",
        host=get_config("web.host"),
        port=int(get_config("web.port")),
        lifespan="off",
    )
