# typing
from typing import Annotated

# 3rd party
from fastapi import Depends

# api
from xthulu.models.user import User
from xthulu.web.auth import login_user

# local
from .. import api


@api.get("/")
def userland_demo(user: Annotated[User, Depends(login_user)]):
    return {
        "userland": True,
        "whoami": user.name,
    }