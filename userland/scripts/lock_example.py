"""Lock example"""

# stdlib
from asyncio import sleep

# api
from xthulu.ssh.context import SSHContext


async def main(cx: SSHContext):
    cx.echo(
        cx.term.normal,
        "\r\n\r\n",
        cx.term.bright_white_on_yellow_underline(" Shared locks demo "),
        "\r\n\r\n",
    )

    with cx.lock("testing") as l:
        if l:
            if cx.encoding == "utf-8":
                cx.echo("🔒 ")

            cx.echo("Lock acquired; press any key to release\r\n")
            await cx.term.inkey()

            if cx.encoding == "utf-8":
                cx.echo("🔥 ")

            cx.echo("Lock released!\r\n")
            await sleep(1)

            return

    if cx.encoding == "utf-8":
        cx.echo("❌ ")

    cx.echo("Failed to acquire lock\r\n")
