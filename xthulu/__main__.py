"xthulu main entry point"

# stdlib
import asyncio as aio
import crypt
import functools
import sys
# 3rd party
import asyncssh
# local
from . import config
from .terminal import AsyncTerminal

#:
passwords = {'guest': ''}


class XthuluSSHServer(asyncssh.SSHServer):

    "xthulu SSH Server"

    def connection_made(self, conn):
        "Connection opened"

        print('Connection from %s' % conn.get_extra_info('peername')[0])

    def connection_lost(self, exc):
        "Connection closed"

        if exc:
            print('Error: %s' % str(exc), file=sys.stderr)

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
        echo = lambda x: proc.stdout.write(x)
        echo(term.normal)
        echo('Connected: %s\n' %
             term.bright_blue(proc.get_extra_info('username')))

        while True:
            if proc.is_closing():
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

                return

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

loop = aio.get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error: %s' % str(exc))

loop.run_forever()
