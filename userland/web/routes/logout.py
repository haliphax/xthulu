"""Web chat"""

# stdlib
from typing import Annotated

# 3rd party
from fastapi import Depends, HTTPException

# api
from xthulu.models.user import User
from xthulu.web.auth import login_user

# local
from .. import api


@api.get("/logout/")
def chat(user: Annotated[User, Depends(login_user)]):
    """End the user session."""

    raise HTTPException(status_code=401)
