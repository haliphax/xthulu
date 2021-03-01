"seed method"

# stdlib
import asyncio as aio
from inspect import isclass
# local
from xthulu import config, db


def seed():
    loop = aio.get_event_loop()

    async def f():
        await db.set_bind(config['db']['bind'])
        models = __import__('userland.models', fromlist=('*',))

        for m in dir(models):
            model = getattr(models, m)

            if not (isclass(model) and issubclass(model, db.Model)):
                continue

            print(f'- {model.__name__}')
            await model.gino.create()

    loop.run_until_complete(f())


if __name__ == '__main__':
    seed()
