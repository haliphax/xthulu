"""Web server module"""

# stdlib
from asyncio import new_event_loop

# 3rd party
from apiflask import APIBlueprint
from uvicorn import run

# local
from ..configuration import get_config
from ..resources import Resources

app = Resources().app
"""Web application"""

api = APIBlueprint("api", __name__, url_prefix="/api")
"""Root blueprint"""


@api.route("/")
def index():
    """Demonstration index route."""

    return {"xthulu": True}


def start_server():
    """Run web server via uvicorn server."""

    async def bind_db():
        await Resources().db.set_bind(get_config("db.bind"))

    new_event_loop().run_until_complete(bind_db())
    run(
        "xthulu.web.asgi:asgi_app",
        host=get_config("web.host"),
        port=int(get_config("web.port")),
    )
