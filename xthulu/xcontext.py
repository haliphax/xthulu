"xthulu context class module"

# stdlib
from collections import namedtuple
# local
from . import log as syslog
from .exceptions import Goto, ProcessClosing
from .structs import EventData, Script


class XthuluContext(object):

    "Context object for SSH sessions"

    #: SSHServerProcess
    proc = None
    #: AsyncTerminal
    term = None
    #: Script stack
    stack = []
    #: Event queue for this session
    events = []

    def __init__(self, proc, *args, **kwargs):
        self.proc = proc

        for k in kwargs.keys():
            setattr(self, k, kwargs[k])

    @property
    def username(self):
        "Client username"

        return self.proc.get_extra_info('username')

    @property
    def remote_ip(self):
        "Remote IP address of client"

        return self.proc.get_extra_info('peername')[0]

    def echo(self, text):
        "Echo text to the terminal"

        self.proc.stdout.write(text)

    async def gosub(self, script, *args, **kwargs):
        "Execute script and return result"

        script = Script(name=script, args=args, kwargs=kwargs)

        return await self.runscript(script)

    def goto(self, script, *args, **kwargs):
        "Switch to script and clear stack"

        raise Goto(script, *args, **kwargs)

    def log(self, level, message):
        "Log message with username@host"

        func = getattr(syslog, level)
        func('{}@{} {}'.format(self.username, self.remote_ip, message))

    async def runscript(self, script):
        "Run script and return result; used by :meth:`goto` and :meth:`gosub`"

        self.log('info', 'Running {}'.format(script))
        imp = __import__('scripts', fromlist=(script.name,))

        try:
            return await getattr(imp, script.name).main(self, *script.args,
                                                        **script.kwargs)
        except (ProcessClosing, Goto):
            raise
        except Exception as exc:
            self.echo(self.term.bright_red_on_black('Exception in {}\n'
                                                    .format(script.name)))
            self.log('exception', exc)
