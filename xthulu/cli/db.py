"""Database CLI"""

# stdlib
from asyncio import get_event_loop
from importlib import import_module

# 3rd party
from asyncpg import DuplicateTableError, UniqueViolationError
from click import confirm, echo, group, option

# local
from ..resources import Resources

db = Resources().db


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

    async def f():
        await db.set_bind(db.bind)
        echo("Creating database and tables")

        try:
            await db.gino.create_all()
        except DuplicateTableError:
            echo("Table already exists")

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

    async def f():
        import_module("...models", __name__)

        # try to load userland models for destruction
        try:
            import_module("userland.models")
        except ImportError:
            pass

        await db.set_bind(db.bind)
        echo("Dropping database tables")
        await db.gino.drop_all()

    if confirmed or confirm(
        "Are you sure you want to destroy the database tables?"
    ):
        get_event_loop().run_until_complete(f())


def _seed():
    from ..models import User

    async def f():
        await db.set_bind(db.bind)

        echo("Creating guest user")
        pwd, salt = User.hash_password("guest")

        try:
            await User.create(
                name="guest",
                email="guest@localhost.localdomain",
                password=pwd,
                salt=salt,
            )
        except UniqueViolationError:
            echo("User already exists")
            return

        echo("Creating user with password")
        pwd, salt = User.hash_password("user")
        await User.create(
            name="user",
            email="user@localhost.localdomain",
            password=pwd,
            salt=salt,
        )

    get_event_loop().run_until_complete(f())


@cli.command()
def seed():
    """Initialize database with starter data."""

    _seed()
