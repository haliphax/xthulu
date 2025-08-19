"""ASGI entry point tests"""

# 3rd party
from fastapi import FastAPI

# local
from xthulu.web.asgi import app  # noqa: F401


def test_asgi_has_app():
    """The ASGI module should produce an 'app' FastAPI object."""

    # assert
    assert isinstance(app, FastAPI)
