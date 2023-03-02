"""xthulu main entry point"""

# stdlib
from asyncio import get_event_loop
from signal import SIGTERM
import sys

# 3rd party
import asyncssh
import click

# local
from . import db
from .configuration import get_config
from .logger import log
from .ssh import start_server as start_ssh
from .web import start_server as start_web

loop = get_event_loop()


@click.group()
def cli():
    """xthulu community server command line utility"""


@cli.command()
def ssh():
    """Start SSH server process"""

    def shutdown():
        from .locks import _Locks, expire

        log.info("Shutting down")

        for owner in _Locks.locks.copy().keys():
            expire(owner)

        loop.stop()

    loop.add_signal_handler(SIGTERM, shutdown)

    try:
        loop.run_until_complete(start_ssh())
    except (OSError, asyncssh.Error) as exc:
        sys.exit(f"Error: {exc}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


@cli.command()
def web():
    """Start web server process"""

    start_web()


@cli.command()
def db_create():
    """Create database tables"""

    from . import models  # noqa: F401

    async def f():
        click.echo("Creating database")
        await db.gino.create_all()  # type: ignore

    loop.run_until_complete(f())


@cli.command()
def db_init():
    """Initialize database with starter data"""

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
    """Main method for CLI; binds to the database before invoking methods."""

    async def f():
        await db.set_bind(get_config("db.bind"))

    loop.run_until_complete(f())
    cli()


if __name__ == "__main__":
    main()
