"""Command line database module"""

# stdlib
from asyncio import get_event_loop
from importlib import import_module
from inspect import isclass

# 3rd party
from click import confirm, echo, group

# api
from xthulu.resources import Resources


async def _get_models():
    db = Resources().db
    await db.set_bind(db.bind)
    models = import_module("...models", __name__)

    for m in dir(models):
        model = getattr(models, m)

        if not (isclass(model) and issubclass(model, db.Model)):
            continue

        print(f"- {model.__name__}")

        yield model


@group("db")
def cli():
    """Database commands"""


@cli.command()
def create():
    """Create database tables."""

    async def f():
        async for model in _get_models():
            await model.gino.create()

    get_event_loop().run_until_complete(f())


@cli.command()
def init():
    """Initialize database with seed data."""

    from ..models import Message, MessageTag, MessageTags

    db = Resources().db

    async def f():
        await db.set_bind(db.bind)
        echo("Posting initial messages")
        tags = (
            await MessageTag.create(name="demo"),
            await MessageTag.create(name="introduction"),
        )

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
def destroy():
    """Drop database tables."""

    async def f():
        async for model in _get_models():
            await model.gino.drop()

    if confirm("Are you sure you want to drop the userland tables?"):
        get_event_loop().run_until_complete(f())
