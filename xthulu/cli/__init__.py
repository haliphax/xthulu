"""Command line module"""

# 3rd party
from click import group

# local
from . import db, ssh, web


@group()
def cli():
    """xthulu community server command line utility"""


cli.add_command(db.cli)
cli.add_command(ssh.cli)
cli.add_command(web.cli)
