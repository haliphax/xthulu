"""Default userland web module"""

# 3rd party
from apiflask import APIBlueprint

# api
from xthulu.models.user import User
from xthulu.web.auth import auth

api = APIBlueprint("userland", __name__, url_prefix="/user")


@api.route("/")
@api.auth_required(auth)
def userland_demo():
    user: User = auth.current_user  # type: ignore
    return {
        "userland": True,
        "whoami": user.name,
    }
