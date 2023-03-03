"""xthulu main entry point"""

# stdlib
from asyncio import new_event_loop
from signal import SIGTERM
import sys

# 3rd party
from asyncssh import Error as AsyncSSHError
from click import echo, group

# local
from .configuration import get_config
from .logger import log
from .resources import Resources
from .ssh import start_server as start_ssh
from .web import start_server as start_web

loop = new_event_loop()
db = Resources().db


async def bind_db():
    await db.set_bind(get_config("db.bind"))


@group()
def main():
    """xthulu community server command line utility"""


@main.command()
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
    except (OSError, AsyncSSHError) as exc:
        sys.exit(f"Error: {exc}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


@main.command()
def web():
    """Start web server process"""

    start_web()


@main.command()
def db_create():
    """Create database tables"""

    from . import models  # noqa: F401

    async def f():
        echo("Creating database and tables")
        await bind_db()
        await db.gino.create_all()  # type: ignore

    loop.run_until_complete(f())


@main.command()
def db_init():
    """Initialize database with starter data"""

    from .models import User

    async def f():
        echo("Creating guest user")
        await bind_db()
        pwd, salt = User.hash_password("guest")
        await User.create(
            name="guest",
            email="guest@localhost.localdomain",
            password=pwd,
            salt=salt,
        )
        echo("Creating user with password")
        pwd, salt = User.hash_password("user")
        await User.create(
            name="user",
            email="user@localhost.localdomain",
            password=pwd,
            salt=salt,
        )

    loop.run_until_complete(f())


if __name__ == "__main__":
    try:
        main()
    finally:
        loop.close()
