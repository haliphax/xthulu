"""Command line database module"""

# stdlib
from asyncio import get_event_loop
from importlib import import_module
from inspect import isclass

# 3rd party
from click import confirm, group

# local
from xthulu.configuration import get_config
from xthulu.resources import Resources


async def _get_models():
    db = Resources().db
    await db.set_bind(get_config("db.bind"))
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
def destroy():
    """Drop database tables."""

    async def f():
        async for model in _get_models():
            await model.gino.drop()

    if confirm("Are you sure you want to drop the userland tables?"):
        get_event_loop().run_until_complete(f())
