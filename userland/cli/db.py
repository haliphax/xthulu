"""Command line database module"""

# stdlib
from asyncio import get_event_loop
from importlib import import_module
from inspect import isclass

# 3rd party
from asyncpg import DuplicateTableError, UniqueViolationError
from click import echo, group, option

# api
from xthulu.resources import Resources

db = Resources().db


async def _get_models():
    await db.set_bind(db.bind)
    models = import_module("...models", __name__)

    for m in dir(models):
        model = getattr(models, m)

        if not (isclass(model) and issubclass(model, db.Model)):
            continue

        yield model


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

    async def f():
        async for model in _get_models():
            print(f"- {model.__name__}")

            try:
                await model.gino.create()
            except DuplicateTableError:
                echo("Table already exists")

    get_event_loop().run_until_complete(f())

    if seed_data:
        _seed()


def _seed():
    from ..models import Message, MessageTag, MessageTags

    db = Resources().db

    async def f():
        await db.set_bind(db.bind)
        echo("Posting initial messages")

        try:
            tags = (
                await MessageTag.create(name="demo"),
                await MessageTag.create(name="introduction"),
            )
        except UniqueViolationError:
            echo("Tags already exist")
            return

        for i in range(100):
            message = await Message.create(
                author_id=1,
                title=f"Hello, world! #{i}",
                content=(
                    "# Hello\n\nHello, world! ✌️\n\n"
                    "## Demo\n\nThis is a demonstration message.\n\n"
                )
                * 20,
            )

            for tag in tags:
                await MessageTags.create(
                    message_id=message.id, tag_name=tag.name
                )

    get_event_loop().run_until_complete(f())


@cli.command()
def seed():
    """Initialize database with seed data."""

    _seed()
