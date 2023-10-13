"""Command line module"""

# stdlib
from asyncio import new_event_loop, set_event_loop_policy

# 3rd party
from click import group
from uvloop import EventLoopPolicy

# local
from . import db, ssh, web


@group()
def cli():
    """xthulu community server command line utility"""


cli.add_command(db.cli)
cli.add_command(ssh.cli)
cli.add_command(web.cli)


def main():
    """Command line entrypoint"""

    set_event_loop_policy(EventLoopPolicy())
    loop = new_event_loop()

    try:
        cli()
    finally:
        loop.close()
