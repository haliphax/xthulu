"xthulu main entry point"

# stdlib
import sys
# 3rd party
from blessed import Terminal
import asyncio
import asyncssh
import crypt
# local
from xthulu import config

#:
passwords = {'guest': ''}

class XthuluSSHServer(asyncssh.SSHServer):

    "xthulu SSH Server"

    def connection_made(self, conn):
        "Connection opened"

        print('Connection from %s' % conn.get_extra_info('peername')[0])

    def connection_lost(self, exc):
        "Connection closed"

        if (exc):
            print('Error: %s' % str(exc), file=sys.stderr)

    def begin_auth(self, username):
        "Check for auth bypass"

        return username not in config['ssh']['auth']['no_password']

    def password_auth_supported(self):
        "Support password authentication"

        return True

    def validate_password(self, username, password):
        "Validate provided password"

        pw = passwords.get(username, '*')

        return crypt.crypt(password, pw) == pw


def handle_client(proc):
    "Client connected"

    term = Terminal(kind=proc.get_terminal_type(), stream=proc.stdout,
                    force_styling=True)
    proc.stdout.write(term.normal)
    proc.stdout.write('Connected: %s\n' %
                       term.bright_blue(proc.get_extra_info('username')))
    proc.exit(0)


async def start_server():
    "throw SSH server into asyncio event loop"

    await asyncssh.create_server(XthuluSSHServer, config['ssh']['host'],
                                 int(config['ssh']['port']),
                                 server_host_keys=config['ssh']['host_keys'],
                                 process_factory=handle_client)

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    sys.exit('Error: %s' % str(exc))

loop.run_forever()
