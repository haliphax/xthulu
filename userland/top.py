"Userland entry point"

# 3rd party
from asyncssh import TerminalSizeChanged
# local
from xthulu import log
from xthulu.events import EventQueues
from xthulu.structs import EventData

async def main(xc):
    xc.echo(xc.term.normal)
    xc.echo('Connected: {}@{}\r\n'
            .format(xc.term.bright_blue(xc.username),
                    xc.term.bright_blue(xc.ip)))

    if xc.encoding == 'utf-8':
        xc.echo('\x1b%G')
    else:
        xc.echo('\x1b%@\x1b(U')

    xc.echo(xc.term.move_x(0) + xc.term.clear_eol)

    for k in xc.proc.env.keys():
        xc.echo('{} = {}\r\n'.format(k, xc.proc.env[k]))

    while True:
        ks = None

        while not ks:
            while not xc.events.empty():
                ev = await xc.events.get()
                xc.echo(repr(ev) + '\r\n')

            ks = await xc.term.inkey(1)

        if ks.code == xc.term.KEY_LEFT:
            xc.echo(xc.term.bright_red('LEFT!\r\n'))
        elif ks.code == xc.term.KEY_RIGHT:
            xc.echo(xc.term.bright_red('RIGHT!\r\n'))
        elif ks.code == xc.term.KEY_UP:
            xc.echo(xc.term.bright_red('UP!\r\n'))
            xc.echo('{}\r\n'.format(await xc.gosub('retval')))
        elif ks.code == xc.term.KEY_DOWN:
            xc.echo(xc.term.bright_red('DOWN!\r\n'))
            await xc.gosub('down', 1, arg2='adsf')
        elif ks.code == xc.term.KEY_ESCAPE:
            xc.echo(xc.term.bright_red('ESCAPE!\r\n'))
            xc.proc.exit(0)
