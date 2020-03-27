"SSH server module"

# stdlib
import asyncio as aio
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
from .models.user import User, hash_password
from .structs import EventData, Script
from .terminal import SlaveProxyTerminal, MasterProxyTerminal


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
    w, h, pw, ph = proc.get_terminal_size()
    proc.env['TERM'] = termtype
    proc.env['COLS'] = w
    proc.env['LINES'] = h
    pipe_master, pipe_slave = Pipe()
    session_stdin = aio.Queue()
    timeout = int(config.get('ssh', {}).get('session', {}).get('timeout', 120))

    async def input_loop():
        "Catch exceptions on stdin and convert to EventData"

        while True:
            try:
                if timeout > 0:
                    r = await aio.wait_for(proc.stdin.readexactly(1), timeout)
                else:
                    r = await proc.stdin.readexactly(1)

                await session_stdin.put(r)

            except aio.streams.IncompleteReadError:
                return

            except aio.futures.TimeoutError:
                cx.echo(cx.term.bold_red_on_black('\r\nTimed out.\r\n'))
                log.warning(f'{cx.user.name}@{cx.sid} timed out')
                proc.close()

                return

            except asyncssh.misc.TerminalSizeChanged as sz:
                cx.term.width = sz.width
                cx.term.height = sz.height
                cx.term.pixel_width = sz.pixwidth
                cx.term.pixel_height = sz.pixheight
                await cx.events.put(EventData('resize',
                                              (sz.width, sz.height,)))

    def terminal_process():
        """
        Avoid Python curses singleton bug by stuffing Terminal in a subprocess
        and proxying calls/responses via Pipe
        """

        subproc_term = SlaveProxyTerminal(termtype, w, h, pw, ph)
        debug_term = config.get('debug', {}).get('term', False)
        inp = None

        while True:
            try:
                given_attr, args, kwargs = pipe_slave.recv()
            except KeyboardInterrupt:
                return

            if debug_term:
                log.debug(f'proxy received: {given_attr}, {args!r}, '
                          f'{kwargs!r}')

            # exit sentinel
            if given_attr is None:
                if debug_term:
                    log.debug(f'term={subproc_term}/pid={os.getpid()} exit')

                break

            # special attribute -- a context manager, enter it naturally, exit
            # unnaturally (even, prematurely), with the exit value ready for
            # our client side, this is only possible because blessed doesn't
            # use any state or time-sensitive values, only terminal sequences,
            # and these CM's are the only ones without side-effects.
            if given_attr.startswith('!CTX'):
                # here, we feel the real punishment of side-effects...
                sideeffect_stream = subproc_term.stream.getvalue()
                assert not sideeffect_stream, ('should be empty',
                                               sideeffect_stream)

                given_attr = given_attr[len('!CTX'):]
                if debug_term: log.debug(f'context attr: {given_attr}')

                with getattr(subproc_term, given_attr)(*args, **kwargs) \
                        as enter_result:
                    enter_side_effect = subproc_term.stream.getvalue()
                    subproc_term.stream.truncate(0)
                    subproc_term.stream.seek(0)

                    if debug_term:
                        log.debug('enter_result, enter_side_effect = '
                                  f'{enter_result!r}, {enter_side_effect!r}')

                    pipe_slave.send((enter_result, enter_side_effect))

                exit_side_effect = subproc_term.stream.getvalue()
                subproc_term.stream.truncate(0)
                subproc_term.stream.seek(0)
                pipe_slave.send(exit_side_effect)

            elif given_attr.startswith('!CALL'):
                given_attr = given_attr[len('!CALL'):]
                matching_attr = getattr(subproc_term, given_attr)
                if debug_term: log.debug(f'callable attr: {given_attr}')
                pipe_slave.send(matching_attr(*args, **kwargs))

            else:
                if debug_term: log.debug(f'attr: {given_attr}')
                assert len(args) == len(kwargs) == 0, (args, kwargs)
                matching_attr = getattr(subproc_term, given_attr)
                if debug_term: log.debug(f'value: {matching_attr!r}')
                pipe_slave.send(matching_attr)


    async def main_process():
        "Userland script stack; main process"

        pt = Process(target=terminal_process)
        pt.start()
        cx.term = MasterProxyTerminal(session_stdin, proc.stdout, cx.encoding,
                                      pipe_master, w, h, pw, ph)
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
            pipe_master.send((None, (), {}))
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
