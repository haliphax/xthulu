"SSH server module"

# stdlib
import asyncio as aio
from multiprocessing import Process, Pipe
import sys
# 3rd party
import asyncssh
from sqlalchemy import func
# local
from . import config, db, locks, log
from .context import Context
from .events import EventQueues
from .exceptions import Goto, ProcessClosing
from .models.user import User, hash_password
from .structs import EventData, Script
from .terminal import Terminal, TerminalProxy

top_names = (config['ssh']['userland']['top']
             if 'top' in config['ssh']['userland'] else ('top',))


class SSHServer(asyncssh.SSHServer):

    "xthulu SSH Server"

    _username = None

    def connection_made(self, conn):
        "Connection opened"

        self._peername = conn.get_extra_info('peername')
        self._sid = '{}:{}'.format(*self._peername)
        EventQueues.q[self._sid] = aio.Queue()
        log.info('{} connecting'.format(self._peername[0]))

    def connection_lost(self, exc):
        "Connection closed"

        del EventQueues.q[self._sid]
        locks.expire(self._sid)

        if exc:
            log.error('Error: {}'.format(exc))

        log.info('{}@{} disconnected'.format(self._username,
                                             self._peername[0]))

    def begin_auth(self, username):
        "Check for auth bypass"

        self._username = username
        pwd_required = True

        if ('no_password' in config['ssh']['auth'] and
                username in config['ssh']['auth']['no_password']):
            log.info('No password required for {}'.format(username))
            pwd_required = False

        log.info('{}@{} connected'.format(username, self._peername[0]))

        return pwd_required

    def password_auth_supported(self):
        "Support password authentication"

        return True

    async def validate_password(self, username, password):
        "Validate provided password"

        u = await (User.query.where(func.lower(User.name) == username.lower())
                   .gino.first())

        if u is None:
            log.warn('User {} does not exist'.format(username))

            return False

        expected, _ = hash_password(password, u.salt)

        if expected != u.password:
            log.warn('Invalid credentials received for {}'
                     .format(username))

            return False

        log.info('Valid credentials received for {}'.format(username))

        return True


async def handle_client(proc):
    "Client connected"

    cx = Context(proc=proc)

    if 'LANG' not in cx.proc.env or 'UTF-8' not in cx.proc.env['LANG']:
        cx.encoding = 'cp437'

    termtype = cx.proc.get_terminal_type()
    w, h, _, _ = proc.get_terminal_size()
    proc.env['TERM'] = termtype
    proc.env['COLS'] = w
    proc.env['LINES'] = h
    proxy_in, proxy_out = Pipe()
    stdin = aio.Queue()

    async def input_loop():
        "Catch exceptions on stdin and convert to EventData"

        while True:
            try:
                r = await proc.stdin.readexactly(1)
                await stdin.put(r)
            except aio.streams.IncompleteReadError:
                return
            except asyncssh.misc.TerminalSizeChanged as sz:
                cx.term._width = sz.width
                cx.term._height = sz.height
                await cx.events.put(EventData('resize',
                                              (sz.width, sz.height,)))

    def terminal_loop():
        """
        Avoid Python curses singleton bug by stuffing Terminal in a subprocess
        and proxying calls/responses via Pipes
        """

        term = Terminal(termtype, proc.stdout)
        debug_proxy = (config['debug']['proxy']
                       if 'debug' in config and 'proxy' in config['debug']
                       else False)
        inp = None

        while True:
            try:
                inp = proxy_out.recv()
            except KeyboardInterrupt:
                return

            if debug_proxy:
                log.debug('proxy received: {}'.format(inp))

            attr = getattr(term, inp[0])

            if callable(attr) or len(inp[1]) or inp[2]:
                if debug_proxy:
                    log.debug('{} callable'.format(inp[0]))

                proxy_out.send(attr(*inp[1], **inp[2]))
            else:
                if debug_proxy:
                    log.debug('{} not callable'.format(inp[0]))

                proxy_out.send(attr)

    async def main_process():
        "Userland script stack; main process"

        pt = Process(target=terminal_loop)
        pt.start()
        cx.term = TerminalProxy(stdin, cx.encoding, proxy_in, proxy_out, w, h)
        # prep script stack with top scripts;
        # since we're treating it as a stack and not a queue, add them reversed
        # so they are executed in the order they were defined
        cx.stack = [Script(s, (), {}) for s in reversed(top_names)]

        # main script engine loop
        try:
            while len(cx.stack):
                try:
                    await cx.runscript(cx.stack.pop())
                except Goto as goto_script:
                    cx.stack = [goto_script.value]
                except ProcessClosing:
                    cx.stack = []
        finally:
            pt.terminate()
            proc.close()

    await aio.gather(input_loop(), main_process())


async def start_server():
    "Run init tasks and throw SSH server into asyncio event loop"

    await db.set_bind(config['db']['bind'])
    await asyncssh.create_server(SSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client,
                                 encoding=None)
