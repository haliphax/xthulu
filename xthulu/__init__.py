"xthulu python 3 asyncio BBS software"

# stdlib
import asyncio as aio
import crypt
import functools
import logging
from os import environ
from os.path import dirname, join
import sys
# 3rd party
import asyncssh
from yaml import safe_load
# local
from .terminal import AsyncTerminal

log = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(logging.Formatter(
        '{asctime} {module}.{funcName}: {message}', style='{'))
log.addHandler(streamHandler)
log.setLevel(logging.DEBUG)
config = {}
config_file = (environ['XTHULU_CONFIG'] if 'XTHULU_CONFIG' in environ
               else join(dirname(__file__), '..', 'data', 'config.yml'))

with open(config_file) as f:
    config = safe_load(f)

passwords = {'guest': ''}


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
                await q.put(await proc.stdin.readexactly(1))
            except aio.streams.IncompleteReadError:
                continue

    async def main_process():
        username = proc.get_extra_info('username')
        peername = proc.get_extra_info('peername')[0]
        echo = lambda x: proc.stdout.write(x)
        echo(term.normal)
        echo('Connected: {}@{}\n'
             .format(term.bright_blue(username), term.bright_blue(peername)))

        while True:
            if proc.is_closing():
                log.info('Connection lost: {}@{}'.format(username, peername))

                return

            ks = await term.inkey()

            if ks.code == term.KEY_LEFT:
                echo(term.bright_red('LEFT!\n'))
            elif ks.code == term.KEY_RIGHT:
                echo(term.bright_red('RIGHT!\n'))
            elif ks.code == term.KEY_UP:
                echo(term.bright_red('UP!\n'))
            elif ks.code == term.KEY_DOWN:
                echo(term.bright_red('DOWN!\n'))
            elif ks.code == term.KEY_ESCAPE:
                echo(term.bright_red('ESCAPE!\n'))
                proc.exit(0)

    q = aio.Queue()
    proc.stdin.channel.set_line_mode(False)
    term = AsyncTerminal(kind=proc.get_terminal_type(), keyboard=q,
                         stream=proc.stdout, force_styling=True)
    loop = aio.get_event_loop()
    inp = loop.create_task(stdin_loop())
    out = loop.create_task(main_process())
    aio.wait((inp, out,))


async def start_server():
    "throw SSH server into aio event loop"

    await asyncssh.create_server(XthuluSSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client)
