"""ASGI entrypoint"""

# 3rd party
from asgiref.wsgi import WsgiToAsgi

# local
from . import create_app

asgi_app = WsgiToAsgi(create_app())
"""ASGI web application"""
