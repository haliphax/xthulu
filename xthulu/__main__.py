"""xthulu main entry point"""

# stdlib
from asyncio import new_event_loop, set_event_loop_policy

# 3rd party
from click import group
from uvloop import EventLoopPolicy

# local
from .cli import db, ssh, web

set_event_loop_policy(EventLoopPolicy())
loop = new_event_loop()


@group()
def main():
    """xthulu community server command line utility"""


main.add_command(db.cli)
main.add_command(ssh.cli)
main.add_command(web.cli)

if __name__ == "__main__":
    try:
        main()
    finally:
        loop.close()
