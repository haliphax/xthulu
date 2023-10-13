"""Command line entrypoint"""

# stdlib
from asyncio import new_event_loop, set_event_loop_policy

# 3rd party
from click import group
from uvloop import EventLoopPolicy

# local
from . import db


@group()
def cli():
    """xthulu community server userland command line utility"""


cli.add_command(db.cli)


def main():
    set_event_loop_policy(EventLoopPolicy())
    loop = new_event_loop()

    try:
        cli()
    finally:
        loop.close()
