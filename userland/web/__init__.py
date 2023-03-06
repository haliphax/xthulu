"""Default userland web module"""

# api
from apiflask import APIBlueprint

api = APIBlueprint("userland", __name__, url_prefix="/user")


@api.route("/")
def userland_demo():
    return {"userland": True}
