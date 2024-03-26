"""Messages script"""

# api
from xthulu.ssh.context import SSHContext

# local
from .app import MessagesApp


async def main(cx: SSHContext) -> None:
    cx.console.set_window_title("messages")
    await MessagesApp(
        cx, art_path="userland/artwork/messages.ans", art_encoding="amiga"
    ).run_async()
