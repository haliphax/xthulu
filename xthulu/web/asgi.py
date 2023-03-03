"""ASGI entrypoint"""


def main():
    """Placed within a function for unit testing."""

    # 3rd party
    from asgiref.wsgi import WsgiToAsgi

    # local
    from . import app, api

    app.register_blueprint(api)

    return WsgiToAsgi(app)


asgi_app = main()
"""ASGI web application"""
