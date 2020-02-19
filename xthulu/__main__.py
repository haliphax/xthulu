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
    'Start SSH server process'

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
    'Create database tables'

    from . import models

    async def f():
        click.echo('Creating database')
        await db.gino.create_all()

    loop.run_until_complete(f())


@cli.command()
def db_init():
    'Initialize database with starter data'

    from .models.user import User, hash_password

    async def f():
        click.echo('Creating guest user')
        pwd, salt = hash_password('guest')
        await User.create(name='guest', email='guest@localhost.localdomain',
                          password=pwd, salt=salt)
        click.echo('Creating user with password')
        pwd, salt = hash_password('user')
        await User.create(name='user', email='user@localhost.localdomain',
                          password=pwd, salt=salt)

    loop.run_until_complete(f())


def main():
    async def f():
        await db.set_bind(config['db']['bind'])

    loop.run_until_complete(f())
    cli()


if __name__ == '__main__':
    main()
