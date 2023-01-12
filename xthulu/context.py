"xthulu context class module"

# stdlib
import asyncio as aio
from codecs import decode
from functools import partial, singledispatch
from imp import find_module, load_module
import logging
import subprocess
import sys
from typing import List, Tuple, Union

# 3rd party
from asyncssh import SSHServerProcess

# local
from . import config, db, locks, log as syslog
from .events import EventQueue
from .exceptions import Goto, ProcessClosing
from .models import User
from .structs import Script


class _LockManager(object):
    def __init__(self, sid: str, name: str):
        self.sid = sid
        self.name = name

    def __enter__(self, *args, **kwargs):
        return locks.get(self.sid, self.name)

    def __exit__(self, *args, **kwargs):
        return locks.release(self.sid, self.name)


class Context(object):

    "Context object for SSH sessions"

    #: Script stack
    stack = []
    #: User object (assigned at _init)
    user: User = None
    _sid: str = None

    def __init__(self, proc, encoding="utf-8"):
        _peername = proc.get_extra_info("peername")
        _username = proc.get_extra_info("username")
        #: SSHServerProcess for session
        self.proc: SSHServerProcess = proc
        self._sid: str = "{}:{}".format(*_peername)
        #: Encoding for session
        self.encoding: str = encoding
        #: Remote IP address
        self.ip: str = _peername[0]
        #: Logging facility
        self.log: logging.Logger = logging.getLogger(self.sid)
        #: Events queue
        self.events: EventQueue = EventQueue(self.sid)
        #: Environment variables
        self.env: dict = proc.env

        # set up logging
        if not self.log.filters:
            self.log.addFilter(ContextLogFilter(_username, self.ip))
            streamHandler = logging.StreamHandler(sys.stdout)
            streamHandler.setFormatter(
                logging.Formatter(
                    "{asctime} {levelname:<7} {module}.{funcName}: "
                    "{username}@{ip} {message}",
                    style="{",
                )
            )
            self.log.addHandler(streamHandler)
            self.log.setLevel(syslog.getEffectiveLevel())

    async def _init(self):
        "Asynchronous initialization routine"

        _username = self.proc.get_extra_info("username")
        self.user = await (
            User.query.where(
                db.func.lower(User.name) == _username.lower()
            ).gino.first()
        )
        self.log.debug(repr(self.user))

    # read-only
    @property
    def sid(self) -> str:
        "Session ID (IP:PORT)"

        return self._sid

    def echo(self, text: str, encoding=None) -> None:
        """
        Echo text to the terminal

        :param text: The text to echo
        """

        if text is None:
            return

        if encoding is not None:
            text = decode(bytes(text, encoding), encoding)

        self.proc.stdout.write(text.encode(self.encoding))

    async def gosub(self, script: Script, *args, **kwargs) -> any:
        """
        Execute script and return result

        :param script: The userland script to execute
        :returns: The return value from the script (if any)
        """

        script = Script(script, args, kwargs)

        return await self.runscript(script)

    def goto(self, script: Script, *args, **kwargs) -> None:
        """
        Switch to script and clear stack

        :param script: The userland script to execute
        """

        raise Goto(script, *args, **kwargs)

    @property
    def lock(self) -> bool:
        """
        Session lock context manager

        :param name: The name of the lock to attempt
        :returns: Whether or not the lock was granted
        """

        return partial(_LockManager, self.sid)

    def get_lock(self, name: str) -> bool:
        """
        Acquire lock on behalf of session user

        :param name: The name of the lock to attempt
        :returns: Whether or not the lock was granted
        """

        return locks.get(self.sid, name)

    def release_lock(self, name: str) -> bool:
        """
        Release lock on behalf of session user

        :param name: The name of the lock to release
        :returns: Whether or not the lock was valid to begin with
        """

        return locks.release(self.sid, name)

    async def redirect(
        self, proc: Union[subprocess.Popen, List, Tuple, str]
    ) -> None:
        """
        Redirect context IO to other process; convenience method which wraps
        AsyncSSH's redirection routine

        :param proc: The process to redirect to
        """

        @singledispatch
        async def f(proc):
            raise NotImplemented("proc must be Popen, tuple, list, or str")

        @f.register(subprocess.Popen)
        async def _(proc):
            await self.proc.redirect(
                stdin=proc.stdin,
                stdout=proc.stdout,
                stderr=proc.stderr,
                send_eof=False,
            )
            await self.proc.stdout.drain()
            await self.proc.stderr.drain()
            await self.proc.redirect(stdin=subprocess.PIPE)

        @f.register(tuple)
        @f.register(list)
        @f.register(str)
        async def _(proc):
            p = subprocess.Popen(
                proc,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=False,
            )
            await self.redirect(p)

        await f(proc)

    async def runscript(self, script: Script) -> any:
        """
        Run script and return result; used by :meth:`goto` and :meth:`gosub`

        :param script: The userland script to run
        :returns: The return value of the script (if any)
        """

        self.log.info(f"Running {script}")
        split = script.name.split(".")
        found = None
        mod = None

        for seg in split:
            if mod is not None:
                found = find_module(seg, mod.__path__)
            else:
                found = find_module(seg, config["ssh"]["userland"]["paths"])

            mod = load_module(seg, *found)

        try:
            return await mod.main(self, *script.args, **script.kwargs)
        except (ProcessClosing, Goto):
            raise
        except Exception as exc:
            self.log.exception(exc)
            self.echo(
                self.term.bold_red_on_black(
                    f"\r\nException in {script.name}\r\n"
                )
            )
            await aio.sleep(3)


class ContextLogFilter(logging.Filter):

    "Custom logging.Filter that injects username and remote IP address"

    #: The context user's username
    username: str = None
    #: The context user's IP address
    ip: str = None

    def __init__(self, username: str, ip: str):
        self.username = username
        self.ip = ip

    def filter(self, record: logging.LogRecord):
        "Filter log record"

        record.username = self.username
        record.ip = self.ip

        return True
