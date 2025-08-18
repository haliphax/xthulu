"""Command line module"""

# 3rd party
from click import group

# local
from . import db


@group()
def cli():
    """xthulu community server userland command line utility"""


cli.add_command(db.cli)
