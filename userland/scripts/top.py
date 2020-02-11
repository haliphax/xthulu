"Userland entry point"

from xthulu import log

async def main(xc):
    echo = lambda x: xc.proc.stdout.write(x)
    term = xc.term
    echo(term.normal)
    echo('Connected: {}@{}\n'
         .format(term.bright_blue(xc.username),
                 term.bright_blue(xc.remote_ip)))

    while True:
        if xc.proc.is_closing():
            log.info('Connection lost: {}@{}'
                     .format(xc.username, xc.remote_ip))

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
            xc.proc.exit(0)
