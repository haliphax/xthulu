"""Web authentication"""

# stdlib
from secrets import compare_digest
from typing import Annotated

# 3rd party
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import func, select

# local
from ..configuration import get_config
from ..models.user import User
from ..resources import get_session

auth = HTTPBasic()


async def login_user(
    credentials: Annotated[HTTPBasicCredentials, Depends(auth)],
):
    """
    HTTP Basic authentication routine. Use as a dependency in route arguments to
    require authentication.

    Returns:
        A `xthulu.models.user.User` model object for the authenticated user.
    """

    async with get_session() as db:
        user = (
            await db.exec(
                select(User).where(
                    func.lower(User.name) == credentials.username.lower()
                )
            )
        ).one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

    no_password = set(get_config("ssh.auth.no_password", []))

    if user.name in no_password:
        return user

    expected, _ = User.hash_password(credentials.password, user.salt)
    assert user.password

    if not compare_digest(expected, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Basic"},
        )

    return user
