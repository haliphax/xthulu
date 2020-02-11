"SSH server module"

# stdlib
import asyncio as aio
import crypt
import sys
# 3rd party
import asyncssh
# local
from . import config, log
from .exceptions import Goto, Event, ProcessClosingException
from .structs import EventData, Script
from .terminal import AsyncTerminal
from .xcontext import XthuluContext


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

        if ('no_password' in config['ssh']['auth'] and
                username in config['ssh']['auth']['no_password']):
            log.info('No password required for {}'.format(username))
            return False

        return True

    def password_auth_supported(self):
        "Support password authentication"

        return True

    def validate_password(self, username, password):
        "Validate provided password"

        pw = passwords.get(username)

        if crypt.crypt(password, pw) == pw:
            log.info('Valid credentials received for {}'.format(username))
            return True

        log.info('Invalid credentials received for {}'.format(username))
        return False


def handle_client(proc):
    "Client connected"

    async def yield_func():
        "Yield function for checking events, etc."

        while not xc.events.empty():
            raise await xc.events.get()

    async def stdin_loop():
        "Handle input"

        while True:
            if proc.stdin.at_eof():
                proc.close()

            if proc.is_closing():
                return

            try:
                r = await aio.wait_for(proc.stdin.read(1), timeout=1)

                if r is not None:
                    await xc.keyboard.put(r)
            except aio.futures.TimeoutError:
                pass
            except asyncssh.misc.TerminalSizeChanged:
                # TODO update AsyncTerminal size
                await xc.events.put(Event('resize', None))

    async def main_process():
        "Main client process"

        username = xc.username
        remote_ip = xc.remote_ip
        top_names = (config['ssh']['userland']['top']
                     if 'userland' in config['ssh'] and
                     'top' in config['ssh']['userland'] else ('top',))

        # prep script stack with top scripts
        for s in top_names:
            xc.stack.append(Script(name=s, args=(), kwargs={}))

        # main script engine loop
        while len(xc.stack):
            try:
                script = xc.stack.pop()
                await xc.runscript(script)
            except Goto as goto_script:
                xc.stack = [goto_script.value]
            except ProcessClosingException:
                log.info('Connection closed: {}@{}'
                         .format(username, remote_ip))
                xc.stack = []

        xc.proc.close()

    loop = aio.get_event_loop()
    proc.stdin.channel.set_line_mode(False)
    xc = XthuluContext(proc=proc)
    term = AsyncTerminal(kind=proc.get_terminal_type(), keyboard=xc.keyboard,
                         proc=proc, stream=proc.stdout, force_styling=True,
                         yield_func=yield_func)
    xc.term = term
    inp = loop.create_task(stdin_loop())
    out = loop.create_task(main_process())
    aio.wait((inp, out,))


async def start_server():
    "throw SSH server into aio event loop"

    await asyncssh.create_server(XthuluSSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client)
