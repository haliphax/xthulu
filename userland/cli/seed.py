"""seed method"""

# stdlib
from asyncio import new_event_loop
from inspect import isclass

# local
from xthulu.configuration import get_config
from xthulu.resources import Resources


async def seed():
    """Seed userland model data."""

    db = Resources().db
    await db.set_bind(get_config("db.bind"))
    models = __import__("userland.models", fromlist=("*",))

    for m in dir(models):
        model = getattr(models, m)

        if not (isclass(model) and issubclass(model, db.Model)):
            continue

        print(f"- {model.__name__}")
        await model.gino.create()


if __name__ == "__main__":
    new_event_loop().run_until_complete(seed())
