"""Web authentication"""

# 3rd party
from apiflask import HTTPBasicAuth

# local
from ..configuration import get_config
from ..models.user import User
from ..resources import Resources

auth = HTTPBasicAuth()
db = Resources().db


@auth.verify_password
async def verify_password(username: str, password: str) -> User | None:
    user: User | None = await db.one_or_none(
        User.query.where(User.name == username)
    )

    if not user:
        return None

    guests: set[str] = set(get_config("ssh.auth.no_password", []))

    if user.name in guests:
        return user

    expected, _ = User.hash_password(password, user.salt)

    if expected != user.password:
        return None

    return user


@auth.get_user_roles
async def get_user_roles(user: User) -> list[str]:
    return []
