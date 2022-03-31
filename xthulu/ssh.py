"SSH server module"

# stdlib
import asyncio as aio
from datetime import datetime
from multiprocessing import Process, Pipe
import os
# 3rd party
import asyncssh
from sqlalchemy import func
# local
from . import config, db, locks, log
from .context import Context
from .events import EventQueues
from .exceptions import Goto, ProcessClosing
from .models.user import User
from .structs import EventData, Script
from .terminal import ProxyTerminal, terminal_process


class SSHServer(asyncssh.SSHServer):

    "xthulu SSH Server"

    _username = None

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        "Connection opened"

        self._peername = conn.get_extra_info('peername')
        self._sid = '{}:{}'.format(*self._peername)
        EventQueues.q[self._sid] = aio.Queue()
        log.info(f'{self._peername[0]} connecting')

    def connection_lost(self, exc: Exception):
        "Connection closed"

        del EventQueues.q[self._sid]
        locks.expire(self._sid)

        if exc:
            log.error(f'Error: {exc}')

        log.info(f'{self._username}@{self._peername[0]} disconnected')

    def begin_auth(self, username: str):
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

    async def validate_password(self, username: str, password: str):
        "Validate provided password"

        u = await (User.query.where(func.lower(User.name) == username.lower())
                   .gino.first())

        if u is None:
            log.warn(f'User {username} does not exist')

            return False

        expected, _ = User.hash_password(password, u.salt)

        if expected != u.password:
            log.warn(f'Invalid credentials received for {username}')

            return False

        log.info(f'Valid credentials received for {username}')

        return True


async def handle_client(proc: asyncssh.SSHServerProcess):
    "Client connected"

    cx = Context(proc=proc)
    await cx._init()

    if 'LANG' not in cx.proc.env or 'UTF-8' not in cx.proc.env['LANG']:
        cx.encoding = 'cp437'

    termtype = proc.get_terminal_type()
    w, h, pw, ph = proc.get_terminal_size()
    proxy_pipe, subproc_pipe = Pipe()
    session_stdin = aio.Queue()
    timeout = int(config.get('ssh', {}).get('session', {}).get('timeout', 120))
    await cx.user.update(last=datetime.utcnow()).apply()

    async def input_loop():
        "Catch exceptions on stdin and convert to EventData"

        while True:
            try:
                if timeout > 0:
                    r = await aio.wait_for(proc.stdin.readexactly(1), timeout)
                else:
                    r = await proc.stdin.readexactly(1)

                await session_stdin.put(r)

            except aio.IncompleteReadError:
                return

            except aio.TimeoutError:
                cx.echo(cx.term.bold_red_on_black('\r\nTimed out.\r\n'))
                log.warning(f'{cx.user.name}@{cx.sid} timed out')
                proc.close()

                return

            except asyncssh.misc.TerminalSizeChanged as sz:
                cx.term._width = sz.width
                cx.term._height = sz.height
                cx.term._pixel_width = sz.pixwidth
                cx.term._pixel_height = sz.pixheight
                await cx.events.put(EventData('resize',
                                              (sz.width, sz.height,)))

    async def main_process():
        "Userland script stack; main process"

        tp = Process(target=terminal_process,
                     args=(termtype, w, h, pw, ph, subproc_pipe))
        tp.start()
        cx.term = ProxyTerminal(session_stdin, proc.stdout, cx.encoding,
                                proxy_pipe, w, h, pw, ph)
        # prep script stack with top scripts;
        # since we're treating it as a stack and not a queue, add them reversed
        # so they are executed in the order they were defined
        top_names = (config.get('ssh', {}).get('userland', {})
                     .get('top', ('top',)))
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
            # send sentinel to close child 'term_pipe' process
            proxy_pipe.send((None, (), {}))
            proc.close()

    await aio.gather(input_loop(), main_process())


async def start_server():
    "Run init tasks and throw SSH server into asyncio event loop"

    await db.set_bind(config['db']['bind'])
    log.info('SSH listening on '
             f"{config['ssh']['host']}:{config['ssh']['port']}")
    await asyncssh.create_server(SSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client,
                                 encoding=None)
