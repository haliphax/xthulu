"""Database CLI"""

# stdlib
from asyncio import get_event_loop

# 3rd party
from click import confirm, echo, group, option
from sqlmodel import SQLModel

# local
from ..resources import db_session, Resources


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

    from .. import models  # noqa: F401

    async def f():
        echo("Creating database and tables")

        async with Resources().db.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    get_event_loop().run_until_complete(f())

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
        from .. import models  # noqa: F401

        try:
            from userland import models as user_models  # noqa: F401
        except ImportError:  # pragma: no cover
            pass

        echo("Dropping database tables")

        async with Resources().db.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)

    if confirmed or confirm(
        "Are you sure you want to destroy the database tables?"
    ):
        get_event_loop().run_until_complete(f())


def _seed():
    from ..models import User

    async def f():
        echo("Creating guest user")
        pwd, salt = User.hash_password("guest")

        async with db_session() as db:
            db.add(
                User(
                    name="guest",
                    email="guest@localhost.localdomain",
                    password=pwd,
                    salt=salt,
                )
            )
            await db.commit()

        echo("Creating user with password")
        pwd, salt = User.hash_password("user")

        async with db_session() as db:
            db.add(
                User(
                    name="user",
                    email="user@localhost.localdomain",
                    password=pwd,
                    salt=salt,
                )
            )
            await db.commit()

    get_event_loop().run_until_complete(f())


@cli.command()
def seed():
    """Initialize database with starter data."""

    _seed()
