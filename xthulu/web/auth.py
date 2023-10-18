"""Web authentication"""

# typing
from typing import Annotated

# stdlib
from secrets import compare_digest

# 3rd party
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# local
from ..configuration import get_config
from ..models.user import User
from ..resources import Resources

auth = HTTPBasic()
db = Resources().db


async def login_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(auth)]
):
    await db.set_bind(get_config("db.bind"))

    try:
        user: User | None = await db.one_or_none(
            User.query.where(User.name == credentials.username)
        )
    finally:
        await db.pop_bind().close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

    no_password = set(get_config("ssh.auth.no_password", []))

    if user.name in no_password:
        return user

    expected, _ = User.hash_password(credentials.password, user.salt)

    if not compare_digest(expected, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

    return user
