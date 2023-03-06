"""ASGI entrypoint"""


def main():
    """Placed within a function for unit testing."""

    # stdlib
    from importlib import import_module

    # 3rd party
    from apiflask import APIBlueprint
    from asgiref.wsgi import WsgiToAsgi

    # local
    from ..configuration import get_config
    from ..logger import log
    from . import api, app

    for mod in list(get_config("web.userland.modules", [])):
        loaded = import_module(mod)

        if hasattr(loaded, "api"):
            log.info(f"Loading userland web module: {mod}")
            mod_api: APIBlueprint = getattr(loaded, "api")
            api.register_blueprint(mod_api)

    app.register_blueprint(api)

    return WsgiToAsgi(app)


asgi_app = main()
"""ASGI web application"""
