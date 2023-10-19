# typing
from typing import Annotated

# 3rd party
from fastapi import Depends

# local
from ...models.user import User
from ..schema.index import DemoResponse
from ..auth import login_user
from .. import api


@api.get("/")
def demo(user: Annotated[User, Depends(login_user)]) -> DemoResponse:
    """Demonstration index route."""

    return DemoResponse(whoami=user.name, xthulu=True)
