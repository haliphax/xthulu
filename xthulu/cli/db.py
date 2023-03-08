"""Database CLI"""

# stdlib
from asyncio import get_event_loop

# 3rd party
from click import echo, group

# local
from ..configuration import get_config
from ..resources import Resources


@group("db")
def cli():
    """Database commands"""


@cli.command()
def create():
    """Create database tables"""

    from .. import models  # noqa: F401

    loop = get_event_loop()
    res = Resources()

    async def f():
        await res.db.set_bind(get_config("db.bind"))
        echo("Creating database and tables")
        await res.db.gino.create_all()  # type: ignore

    loop.run_until_complete(f())


@cli.command()
def init():
    """Initialize database with starter data"""

    from ..models import User

    loop = get_event_loop()
    res = Resources()

    async def f():
        await res.db.set_bind(get_config("db.bind"))
        echo("Creating guest user")
        pwd, salt = User.hash_password("guest")
        await User.create(
            name="guest",
            email="guest@localhost.localdomain",
            password=pwd,
            salt=salt,
        )
        echo("Creating user with password")
        pwd, salt = User.hash_password("user")
        await User.create(
            name="user",
            email="user@localhost.localdomain",
            password=pwd,
            salt=salt,
        )

    loop.run_until_complete(f())
