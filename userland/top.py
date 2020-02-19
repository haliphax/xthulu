"Userland entry point"

# 3rd party
from asyncssh import TerminalSizeChanged
# local
from xthulu import log
from xthulu.events import EventQueues
from xthulu.structs import EventData

async def main(cx):
    cx.echo(cx.term.normal)
    cx.echo('Connected: {}@{}\r\n'
            .format(cx.term.bold_blue(cx.username),
                    cx.term.bold_blue(cx.ip)))

    if cx.encoding == 'utf-8':
        cx.echo('\x1b%G')
    else:
        cx.echo('\x1b%@\x1b(U')

    cx.echo(cx.term.move_x(0) + cx.term.clear_eol)

    for k in cx.proc.env.keys():
        cx.echo('{} = {}\r\n'.format(k, cx.proc.env[k]))

    while True:
        ks = None

        while not ks:
            while not cx.events.empty():
                ev = await cx.events.get()
                cx.echo(repr(ev) + '\r\n')

            ks = await cx.term.inkey(1)

        if ks.code == cx.term.KEY_LEFT:
            cx.echo(cx.term.bold_red('LEFT!\r\n'))
        elif ks.code == cx.term.KEY_RIGHT:
            cx.echo(cx.term.bold_red('RIGHT!\r\n'))
        elif ks.code == cx.term.KEY_UP:
            cx.echo(cx.term.bold_red('UP!\r\n'))
            cx.echo('{}\r\n'.format(await cx.gosub('retval')))
        elif ks.code == cx.term.KEY_DOWN:
            cx.echo(cx.term.bold_red('DOWN!\r\n'))
            await cx.gosub('down', 1, arg2='adsf')
        elif ks.code == cx.term.KEY_ESCAPE:
            cx.echo(cx.term.bold_red('ESCAPE!\r\n'))
            cx.proc.exit(0)
