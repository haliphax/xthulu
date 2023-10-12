"""Lock example"""

# api
from xthulu.ssh.context import SSHContext


async def main(cx: SSHContext):
    cx.echo("\n[bright_white on yellow underline] Shared locks demo [/]\n\n")

    with cx.lock("testing") as l:
        if l:
            await cx.inkey(":lock: Lock acquired; press any key to release")
            cx.echo(":fire: Lock released!\n")
            await cx.inkey(timeout=1)

            return

    cx.echo(":cross_mark: Failed to acquire lock\n")
    await cx.inkey(timeout=2)
