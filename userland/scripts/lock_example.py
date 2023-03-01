"""Lock example"""

# api
from xthulu.ssh.context import SSHContext


async def main(cx: SSHContext):
    with cx.lock("testing") as l:
        if not l:
            cx.echo("Unable to acquire lock\r\n")
        else:
            cx.echo("Got lock\r\n")
            await cx.term.inkey()
            cx.echo("Released\r\n")
