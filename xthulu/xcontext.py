"xthulu context class module"

# stdlib
from collections import namedtuple
import logging
import sys
# local
from . import log as syslog
from .events import EventQueues
from .exceptions import Goto, ProcessClosing
from .structs import Script


class XthuluContext(object):

    "Context object for SSH sessions"

    #: Script stack
    stack = []

    def __init__(self, proc, encoding='utf-8'):
        #: SSHServerProcess for session
        self.proc = proc
        #: Encoding for session
        self.encoding = encoding
        #: Username
        self.username = proc.get_extra_info('username')
        #: Remote IP address
        self.ip = proc.get_extra_info('peername')[0]
        #: Logging facility
        self.log = logging.getLogger('xc')
        #: Events queue
        self.events = EventQueues.q['{}:{}'
                .format(*self.proc.get_extra_info('peername'))]

        # set up logging
        self.log.addFilter(XthuluContextLogFilter(self.username, self.ip))
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(logging.Formatter(
                '{asctime} {levelname} {module}.{funcName}: {username}@{ip} '
                '{message}',
                style='{'))
        self.log.addHandler(streamHandler)
        self.log.setLevel(syslog.getEffectiveLevel())

    def echo(self, text):
        "Echo text to the terminal"

        self.proc.stdout.write(text.encode(self.encoding))

    async def gosub(self, script, *args, **kwargs):
        "Execute script and return result"

        script = Script(script, args, kwargs)

        return await self.runscript(script)

    def goto(self, script, *args, **kwargs):
        "Switch to script and clear stack"

        raise Goto(script, *args, **kwargs)

    async def runscript(self, script):
        "Run script and return result; used by :meth:`goto` and :meth:`gosub`"

        self.log.info('Running {}'.format(script))
        imp = __import__('scripts', fromlist=(script.name,))

        try:
            return await getattr(imp, script.name).main(self, *script.args,
                                                        **script.kwargs)
        except (ProcessClosing, Goto):
            raise
        except Exception as exc:
            self.echo(self.term.bright_red_on_black('\r\nException in {}\r\n'
                                                    .format(script.name)))
            self.log.exception(exc)


class XthuluContextLogFilter(logging.Filter):

    "Custom logging.Filter that injects username and remote IP address"

    def __init__(self, username, ip):
        self.username = username
        self.ip = ip

    def filter(self, record):
        "Filter log record"

        record.username = self.username
        record.ip = self.ip
        return True
