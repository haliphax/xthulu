"xthulu main entry point"

# stdlib
import asyncio as aio
import sys
# 3rd party
import asyncssh
import click
# local
from . import config, db, log
from .ssh import start_server

loop = aio.get_event_loop()


@click.group()
def cli():
    pass


@cli.command()
def start():
    try:
        log.info('Starting SSH server')
        loop.run_until_complete(start_server())
    except (OSError, asyncssh.Error) as exc:
        sys.exit('Error: {}'.format(exc))

    try:
        log.info('SSH server is listening')
        loop.run_forever()
    except KeyboardInterrupt:
        log.info('Shutting down')


@cli.command()
def db_create():
    async def f():
        from . import models

        click.echo('Creating database')
        await db.gino.create_all()

    loop.run_until_complete(f())


@cli.command()
def db_dummy():
    async def f():
        from .models import User

        click.echo('Filling with dummy data')
        await User.create(name='guest')

    loop.run_until_complete(f())


if __name__ == '__main__':
    async def f():
        await db.set_bind(config['db']['bind'])

    loop.run_until_complete(f())
    cli()
