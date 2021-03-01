"seed method"

# stdlib
import asyncio as aio
from inspect import isclass
# local
from xthulu import config, db


async def seed():
    await db.set_bind(config['db']['bind'])
    models = __import__('userland.models', fromlist=('*',))

    for m in dir(models):
        model = getattr(models, m)

        if not (isclass(model) and issubclass(model, db.Model)):
            continue

        print(f'- {model.__name__}')
        await model.gino.create()


if __name__ == '__main__':
    aio.get_event_loop().run_until_complete(seed())
