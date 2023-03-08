"""Web server CLI"""

# 3rd party
from click import group

# local
from ..web import start_server


@group("web")
def cli():
    """Web server commands"""


@cli.command()
def start():
    """Start web server process"""

    start_server()
