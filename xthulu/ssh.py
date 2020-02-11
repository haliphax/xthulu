"SSH server module"

# stdlib
import asyncio as aio
import crypt
import sys
# 3rd party
import asyncssh
# local
from . import config, log
from .exceptions import ProcessClosingException
from .terminal import AsyncTerminal
from .xcontext import XthuluContext, Script, Goto


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
            if proc.stdin.at_eof():
                proc.close()

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
        username = xc.username
        remote_ip = xc.remote_ip
        top_name = (config['ssh']['userland']['top']
                    if 'top' in config['ssh']['userland'] else 'top')
        xc.stack.append(Script(name=top_name, args=(), kwargs={}))
        script = None

        while len(xc.stack):
            try:
                script = xc.stack.pop()
                await xc.runscript(script)
            except Goto as goto_script:
                xc.stack = [goto_script.value]
            except ProcessClosingException:
                log.info('Connection lost: {}@{}'.format(username, remote_ip))
                xc.stack = []

        xc.proc.close()

    if 'paths' in config['ssh']['userland']:
        for p in config['ssh']['userland']['paths']:
            sys.path.insert(0, p)

    loop = aio.get_event_loop()
    kbd = aio.Queue()
    proc.stdin.channel.set_line_mode(False)
    term = AsyncTerminal(kind=proc.get_terminal_type(), keyboard=kbd,
                         proc=proc, stream=proc.stdout, force_styling=True)
    xc = XthuluContext(proc=proc, term=term)
    inp = loop.create_task(stdin_loop())
    out = loop.create_task(main_process())
    aio.wait((inp, out,))


async def start_server():
    "throw SSH server into aio event loop"

    await asyncssh.create_server(XthuluSSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client)
