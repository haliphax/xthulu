"""Database CLI"""

# stdlib
from asyncio import get_event_loop
from importlib import import_module

# 3rd party
from click import confirm, echo, group, option

# local
from ..resources import Resources


@group("db")
def cli():
    """Database commands"""


@cli.command()
@option(
    "-s/--seed",
    "seed_data",
    default=False,
    flag_value=True,
    help="Seed the database with default data.",
)
def create(seed_data=False):
    """Create database tables."""

    import_module("...models", __name__)
    loop = get_event_loop()
    res = Resources()

    async def f():
        await res.db.set_bind(res.db.bind)
        echo("Creating database and tables")
        await res.db.gino.create_all()

    loop.run_until_complete(f())

    if seed_data:
        _seed()


@cli.command()
@option(
    "--yes",
    "confirmed",
    default=False,
    flag_value=True,
    help="Skip confirmation.",
)
def destroy(confirmed=False):
    """Drop database tables."""

    import_module("...models", __name__)
    loop = get_event_loop()
    res = Resources()

    async def f():
        await res.db.set_bind(res.db.bind)
        echo("Dropping database tables")
        await res.db.gino.drop_all()

    if confirmed or confirm(
        "Are you sure you want to destroy the database tables?"
    ):
        loop.run_until_complete(f())


def _seed():
    from ..models import User

    loop = get_event_loop()
    res = Resources()

    async def f():
        await res.db.set_bind(res.db.bind)

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


@cli.command()
def seed():
    """Initialize database with starter data."""

    _seed()
