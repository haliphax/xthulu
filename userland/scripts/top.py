"Userland entry point"

# local
from xthulu.exceptions import Event

async def main(xc):
    xc.echo(xc.term.normal)
    xc.echo('Connected: {}@{}\n'
            .format(xc.term.bright_blue(xc.username),
                    xc.term.bright_blue(xc.remote_ip)))
    ks = None

    while True:
        try:
            ks = await xc.term.inkey()
        except Event as event:
            if event.value.name == 'resize':
                xc.echo(xc.term.bright_green('RESIZE!\n'))

            continue

        if ks.code == xc.term.KEY_LEFT:
            xc.echo(xc.term.bright_red('LEFT!\n'))
        elif ks.code == xc.term.KEY_RIGHT:
            xc.echo(xc.term.bright_red('RIGHT!\n'))
        elif ks.code == xc.term.KEY_UP:
            xc.echo(xc.term.bright_red('UP!\n'))
        elif ks.code == xc.term.KEY_DOWN:
            xc.echo(xc.term.bright_red('DOWN!\n'))
            await xc.gosub('down', 1, arg2='adsf')
        elif ks.code == xc.term.KEY_ESCAPE:
            xc.echo(xc.term.bright_red('ESCAPE!\n'))
            xc.proc.exit(0)
