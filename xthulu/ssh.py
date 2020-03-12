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
        log.info(f'{self._peername[0]} connecting')

    def connection_lost(self, exc):
        "Connection closed"

        del EventQueues.q[self._sid]
        locks.expire(self._sid)

        if exc:
            log.error(f'Error: {exc}')

        log.info(f'{self._username}@{self._peername[0]} disconnected')

    def begin_auth(self, username):
        "Check for auth bypass"

        self._username = username
        pwd_required = True

        if ('no_password' in config['ssh']['auth'] and
                username in config['ssh']['auth']['no_password']):
            log.info(f'No password required for {username}')
            pwd_required = False

        log.info(f'{username}@{self._peername[0]} connected')

        return pwd_required

    def password_auth_supported(self):
        "Support password authentication"

        return True

    async def validate_password(self, username, password):
        "Validate provided password"

        u = await (User.query.where(func.lower(User.name) == username.lower())
                   .gino.first())

        if u is None:
            log.warn(f'User {username} does not exist')

            return False

        expected, _ = hash_password(password, u.salt)

        if expected != u.password:
            log.warn(f'Invalid credentials received for {username}')

            return False

        log.info(f'Valid credentials received for {username}')

        return True


async def handle_client(proc):
    "Client connected"

    loop = aio.get_event_loop()
    cx = Context(proc=proc)
    await cx._init()

    if 'LANG' not in cx.proc.env or 'UTF-8' not in cx.proc.env['LANG']:
        cx.encoding = 'cp437'

    termtype = cx.proc.get_terminal_type()
    w, h, _, _ = proc.get_terminal_size()
    proc.env['TERM'] = termtype
    proc.env['COLS'] = w
    proc.env['LINES'] = h
    proxy_pipe, term_pipe = Pipe()
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

    def terminal_process():
        """
        Avoid Python curses singleton bug by stuffing Terminal in a subprocess
        and proxying calls/responses via Pipe
        """

        term = Terminal(termtype, proc.stdout)
        debug_term = config.get('debug', {}).get('term', False)
        inp = None

        while True:
            try:
                inp = term_pipe.recv()
            except KeyboardInterrupt:
                return

            if debug_term:
                log.debug(f'proxy received: {inp}')

            attr = getattr(term, inp[0])

            if callable(attr) or len(inp[1]) or len(inp[2]):
                if debug_term:
                    log.debug(f'{inp[0]} callable')

                term_pipe.send(attr(*inp[1], **inp[2]))
            else:
                if debug_term:
                    log.debug('{inp[0]} not callable')

                term_pipe.send(attr)

    async def main_process():
        "Userland script stack; main process"

        pt = Process(target=terminal_process)
        pt.start()
        cx.term = TerminalProxy(stdin, cx.encoding, proxy_pipe, w, h)
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
            log.debug('Terminal proxy terminated')
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
