"""Default userland web module"""

# stdlib
from importlib import import_module

# 3rd party
from fastapi import APIRouter

api = APIRouter(prefix="/user")
import_module(".routes", __name__)
