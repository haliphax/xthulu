"""Lock example"""

# api
from xthulu.ssh.context import SSHContext


async def main(cx: SSHContext):
    cx.echo("\n\n[bright_white on yellow underline] Shared locks demo [/]\n\n")

    with cx.lock("testing") as l:
        if l:
            lock = "🔒 " if cx.encoding == "utf-8" else ""

            await cx.inkey(f"{lock}Lock acquired; press any key to release")

            if cx.encoding == "utf-8":
                cx.echo("🔥 ")

            cx.echo("Lock released!\n")
            await cx.inkey(timeout=1)

            return

    if cx.encoding == "utf-8":
        cx.echo("❌ ")

    cx.echo("Failed to acquire lock\n")
    await cx.inkey(timeout=2)
