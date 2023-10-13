"""Database CLI"""

# stdlib
from asyncio import get_event_loop
from importlib import import_module

# 3rd party
from click import confirm, echo, group

# local
from ..configuration import get_config
from ..resources import Resources


@group("db")
def cli():
    """Database commands"""


@cli.command()
def create():
    """Create database tables."""

    import_module("...models", __name__)
    loop = get_event_loop()
    res = Resources()

    async def f():
        await res.db.set_bind(get_config("db.bind"))
        echo("Creating database and tables")
        await res.db.gino.create_all()

    loop.run_until_complete(f())


@cli.command()
def destroy():
    """Drop database tables."""

    import_module("...models", __name__)
    loop = get_event_loop()
    res = Resources()

    async def f():
        await res.db.set_bind(get_config("db.bind"))
        echo("Dropping database tables")
        await res.db.gino.drop_all()

    if confirm("Are you sure you want to destroy the database tables?"):
        loop.run_until_complete(f())


@cli.command()
def init():
    """Initialize database with starter data."""

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
