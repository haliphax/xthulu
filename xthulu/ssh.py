"SSH server module"

# stdlib
import asyncio as aio
from collections import namedtuple
import crypt
import sys
# 3rd party
import asyncssh
# local
from . import config, log
from .terminal import AsyncTerminal

ProcBag = namedtuple('ProcBag', ('proc', 'term', 'username', 'remote_ip',))


class XthuluSSHServer(asyncssh.SSHServer):

    "xthulu SSH Server"

    def connection_made(self, conn):
        "Connection opened"

        log.info('Connection from {}'
                 .format(conn.get_extra_info('peername')[0]))

    def connection_lost(self, exc):
        "Connection closed"

        if exc:
            log.error('Error: {}'.format(exc))

    def begin_auth(self, username):
        "Check for auth bypass"

        return username not in config['ssh']['auth']['no_password']

    def password_auth_supported(self):
        "Support password authentication"

        return True

    def validate_password(self, username, password):
        "Validate provided password"

        pw = passwords.get(username)

        return crypt.crypt(password, pw) == pw


def handle_client(proc):
    "Client connected"

    async def stdin_loop():
        while True:
            if proc.is_closing():
                return

            try:
                r = await aio.wait_for(proc.stdin.read(1), timeout=1)

                if r is not None:
                    await kbd.put(r)
            except aio.futures.TimeoutError:
                pass
            except asyncssh.misc.TerminalSizeChanged:
                # TODO session event queue, update AsyncTerminal size
                pass

    async def main_process():
        top_name = (config['ssh']['userland']['top']
                    if 'top' in config['ssh']['userland'] else 'top')
        imp = __import__('scripts', fromlist=(top_name,))
        await getattr(imp, top_name).main(xc)

    if 'paths' in config['ssh']['userland']:
        for p in config['ssh']['userland']['paths']:
            sys.path.insert(0, p)

    loop = aio.get_event_loop()
    kbd = aio.Queue()
    proc.stdin.channel.set_line_mode(False)
    term = AsyncTerminal(kind=proc.get_terminal_type(), keyboard=kbd,
                         stream=proc.stdout, force_styling=True)
    xc = ProcBag(proc=proc, term=term,
                 username=proc.get_extra_info('username'),
                 remote_ip=proc.get_extra_info('peername')[0],)
    inp = loop.create_task(stdin_loop())
    out = loop.create_task(main_process())
    aio.wait((inp, out,))


async def start_server():
    "throw SSH server into aio event loop"

    await asyncssh.create_server(XthuluSSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client)
