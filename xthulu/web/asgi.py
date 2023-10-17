"""ASGI entrypoint"""

# 3rd party
# from asgiref.wsgi import WsgiToAsgi

# local
from . import create_app

app = create_app()

# asgi_app = WsgiToAsgi(app)
# """ASGI web application"""
