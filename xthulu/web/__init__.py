"""Web server module"""

# 3rd party
from apiflask import APIBlueprint, APIFlask
from asgiref.wsgi import WsgiToAsgi
from uvicorn import run

app = APIFlask(__name__)
"""Web application"""

bp = APIBlueprint("root", __name__, url_prefix="/api")
"""Root blueprint"""


@bp.route("/")
def index():
    """Demonstration index route."""

    return {"xthulu": True}


app.register_blueprint(bp)

asgi_app = WsgiToAsgi(app)
"""ASGI application"""


def start_server():
    """Run web server via uvicorn server."""

    run(asgi_app, host="0.0.0.0")
