"xthulu context class module"

# stdlib
from contextlib import contextmanager
from functools import singledispatch
from imp import find_module, load_module
import logging
import subprocess
import sys
# 3rd party
from sqlalchemy import func
# local
from . import config, db, locks, log as syslog
from .events import EventQueue
from .exceptions import Goto, ProcessClosing
from .models import User
from .structs import Script


class Context(object):

    "Context object for SSH sessions"

    #: Script stack
    stack = []
    #: User object (assigned at _init)
    user = None

    def __init__(self, proc, encoding='utf-8'):
        _peername = proc.get_extra_info('peername')
        _username = proc.get_extra_info('username')
        #: SSHServerProcess for session
        self.proc = proc
        #: Session ID (IP:PORT)
        self.sid = '{}:{}'.format(*_peername)
        #: Encoding for session
        self.encoding = encoding
        #: Remote IP address
        self.ip = _peername[0]
        #: Logging facility
        self.log = logging.getLogger(self.sid)
        #: Events queue
        self.events = EventQueue(self.sid)
        #: Environment variables
        self.env = proc.env

        # set up logging
        if not self.log.filters:
            self.log.addFilter(ContextLogFilter(_username, self.ip))
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(logging.Formatter(
                '{asctime} {levelname} {module}.{funcName}: {username}@{ip} '
                '{message}',
                style='{'))
            self.log.addHandler(streamHandler)
            self.log.setLevel(syslog.getEffectiveLevel())

    async def _init(self):
        "Asynchronous initialization routine"

        _username = self.proc.get_extra_info('username')
        self.user = await (User.query.where(func.lower(User.name) ==
            _username.lower()).gino.first())
        self.log.debug(repr(self.user))

    def echo(self, text):
        "Echo text to the terminal"

        if text is None:
            return

        self.proc.stdout.write(text.encode(self.encoding))

    async def gosub(self, script, *args, **kwargs):
        "Execute script and return result"

        script = Script(script, args, kwargs)

        return await self.runscript(script)

    def goto(self, script, *args, **kwargs):
        "Switch to script and clear stack"

        raise Goto(script, *args, **kwargs)

    @contextmanager
    def lock(self, name):
        "Session lock context manager"

        try:
            yield locks.get(self.sid, name)
        finally:
            locks.release(self.sid, name)

    def get_lock(self, name):
        "Acquire lock on behalf of session user"

        return locks.get(self.sid, name)

    def release_lock(self, name):
        "Release lock on behalf of session user"

        return locks.release(self.sid, name)

    async def redirect(self, proc):
        "Redirect context IO to other process"

        @singledispatch
        async def f(proc):
            raise NotImplemented("proc must be Popen, tuple, list, or str")

        @f.register(subprocess.Popen)
        async def _(proc):
            await self.proc.redirect(stdin=proc.stdin, stdout=proc.stdout,
                                     stderr=proc.stderr, send_eof=False)
            await self.proc.stdout.drain()
            await self.proc.stderr.drain()
            await self.proc.redirect(stdin=subprocess.PIPE)

        @f.register(tuple)
        @f.register(list)
        @f.register(str)
        async def _(proc):
            p = subprocess.Popen(proc, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, close_fds=False)
            await self.redirect(p)

        return await f(proc)

    async def runscript(self, script):
        "Run script and return result; used by :meth:`goto` and :meth:`gosub`"

        self.log.info('Running {}'.format(script))
        split = script.name.split('.')
        found = None
        mod = None

        for seg in split:
            if mod is not None:
                found = find_module(seg, mod.__path__)
            else:
                found = find_module(seg, config['ssh']['userland']['paths'])

            mod = load_module(seg, *found)

        try:
            return await mod.main(self, *script.args, **script.kwargs)
        except (ProcessClosing, Goto):
            raise
        except Exception as exc:
            self.echo(self.term.bold_red_on_black(
                '\r\nException in {}\r\n'.format(script.name)))
            self.log.exception(exc)
            await aio.sleep(3)


class ContextLogFilter(logging.Filter):

    "Custom logging.Filter that injects username and remote IP address"

    def __init__(self, username, ip):
        self.username = username
        self.ip = ip

    def filter(self, record):
        "Filter log record"

        record.username = self.username
        record.ip = self.ip
        return True
