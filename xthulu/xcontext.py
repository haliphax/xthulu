"xthulu context class module"

# stdlib
from collections import namedtuple
# local
from . import log
from .exceptions import Goto, ProcessClosingException

Script = namedtuple('Script', ('name', 'args', 'kwargs',))


class XthuluContext(object):

    "Context object for SSH sessions"

    #: SSHServerProcess
    proc = None
    #: AsyncTerminal
    term = None
    #: Script stack
    stack = []

    def __init__(self, proc, term, *args, **kwargs):
        self.proc = proc
        self.term = term

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

    async def runscript(self, script):
        "Run script and return result; used by :meth:`goto` and :meth:`gosub`"

        log.info('Running {}'.format(script))
        imp = __import__('scripts', fromlist=(script.name,))

        try:
            return await getattr(imp, script.name).main(self, *script.args,
                                                        **script.kwargs)
        except (ProcessClosingException, Goto):
            raise
        except Exception as exc:
            self.echo(self.term.bright_red_on_black('Exception in {}\n'
                                                    .format(script.name)))
            log.exception(exc)
