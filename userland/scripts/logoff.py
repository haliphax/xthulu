"""Logoff script"""

# api
from xthulu.ssh.context import SSHContext


async def main(cx: SSHContext):
    cx.echo(cx.term.normal, "\r\n" * 4)
