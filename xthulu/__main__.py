"xthulu main entry point"

# stdlib
import asyncio as aio
from signal import SIGTERM
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
    "xthulu terminal server command line utility"


@cli.command()
def start():
    "Start SSH server process"

    def shutdown():
        log.info("Shutting down")
        loop.stop()

    loop.add_signal_handler(SIGTERM, shutdown)

    try:
        loop.run_until_complete(start_server())
    except (OSError, asyncssh.Error) as exc:
        sys.exit(f"Error: {exc}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    shutdown()


@cli.command()
def db_create():
    "Create database tables"

    from . import models  # noqa: F401

    async def f():
        click.echo("Creating database")
        await db.gino.create_all()  # type: ignore

    loop.run_until_complete(f())


@cli.command()
def db_init():
    "Initialize database with starter data"

    from .models.user import User

    async def f():
        click.echo("Creating guest user")
        pwd, salt = User.hash_password("guest")
        await User.create(
            name="guest",
            email="guest@localhost.localdomain",
            password=pwd,
            salt=salt,
        )
        click.echo("Creating user with password")
        pwd, salt = User.hash_password("user")
        await User.create(
            name="user",
            email="user@localhost.localdomain",
            password=pwd,
            salt=salt,
        )

    loop.run_until_complete(f())


def main():
    async def f():
        await db.set_bind(config["db"]["bind"])

    loop.run_until_complete(f())
    cli()


if __name__ == "__main__":
    main()
