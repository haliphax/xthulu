# typing
from typing import Annotated

# 3rd party
from fastapi import Depends

# local
from ...models.user import User
from ..auth import login_user
from .. import api


@api.get("/")
def demo(user: Annotated[User, Depends(login_user)]):
    """Demonstration index route."""

    return {
        "whoami": user.name,
        "xthulu": True,
    }
