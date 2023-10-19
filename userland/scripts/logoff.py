"""Log-off script"""

# api
from xthulu.ssh.context import SSHContext
from xthulu.ssh.console.art import scroll_art


async def main(cx: SSHContext) -> None:
    await scroll_art(cx, "userland/artwork/logoff.ans", "amiga")
