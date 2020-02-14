"SSH server module"

# stdlib
import asyncio as aio
import crypt
from multiprocessing import Process, Pipe
import sys
# 3rd party
import asyncssh
# local
from . import config, log
from .exceptions import Goto, ProcessClosing
from .structs import Script
from .terminal import Terminal, TerminalProxy
from .xcontext import XthuluContext


class XthuluSSHServer(asyncssh.SSHServer):

    "xthulu SSH Server"

    def connection_made(self, conn):
        "Connection opened"

        log.info('Connection from {}'
                 .format(conn.get_extra_info('peername')[0]))
        self._conn = conn

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

    def session_requested(self):
        "Create new channel and session"

        chan = self._conn.create_server_channel(encoding='iso-8859-1')

        return (chan, asyncssh.SSHSession())


def handle_client(proc):
    "Client connected"

    async def main_process():
        "Main client process"

        xc = XthuluContext(proc=proc)

        if 'LANG' not in xc.proc.env or 'UTF-8' not in xc.proc.env['LANG']:
            xc.encoding = 'cp437'

        termtype = xc.proc.get_terminal_type()
        proc.env['TERM'] = termtype

        def terminal_loop():
            term = Terminal(termtype, proc.stdin, proc.stdout)
            inner_loop = aio.new_event_loop()

            while True:
                inp = proxy_out.recv()
                log.debug('proxy received: {}'.format(inp))
                attr = getattr(term, inp[0])

                if callable(attr) or len(inp[1]) or inp[2]:
                    log.debug('{} callable'.format(inp[0]))
                    proxy_out.send(attr(*inp[1], **inp[2]))
                else:
                    log.debug('{} not callable'.format(inp[0]))
                    proxy_out.send(attr)

        pt = Process(target=terminal_loop)
        pt.start()
        xc.term = TerminalProxy(proc.stdin, xc.encoding, proxy_in, proxy_out)
        username = xc.username
        remote_ip = xc.remote_ip
        top_names = (config['ssh']['userland']['top']
                     if 'userland' in config['ssh'] and
                     'top' in config['ssh']['userland'] else ('top',))

        # prep script stack with top scripts;
        # since we're treating it as a stack and not a queue, add them in
        # reverse order so they are executed in the order they were defined
        for s in reversed(top_names):
            xc.stack.append(Script(name=s, args=(), kwargs={}))

        # main script engine loop
        try:
            while len(xc.stack):
                try:
                    script = xc.stack.pop()
                    await xc.runscript(script)
                except Goto as goto_script:
                    xc.stack = [goto_script.value]
                except ProcessClosing:
                    xc.stack = []
        finally:
            log.info('{}@{} disconnected'.format(username, remote_ip))
            pt.terminate()
            proc.close()

    proxy_in, proxy_out = Pipe()
    loop = aio.get_event_loop()
    t_main = loop.create_task(main_process())
    aio.wait(t_main)


async def start_server():
    "throw SSH server into aio event loop"

    await asyncssh.create_server(XthuluSSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client,
                                 encoding=None)
