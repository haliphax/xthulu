"Userland entry point"

# local
from xthulu.ui import LineEditor


async def main(cx):
    if cx.encoding == 'utf-8':
        cx.echo('\x1b%G')
    else:
        cx.echo('\x1b%@\x1b(U')

    cx.echo(cx.term.normal +
            '\r\nConnected: {}@{}\r\n'
            .format(cx.term.bold_blue(cx.user.name),
                    cx.term.bold_blue(cx.ip)))
    led = LineEditor(cx.term, 20, color='bold_white_on_green',
                     value=['testing this thing'])

    for k in cx.env.keys():
        cx.echo(f'{k} = {cx.env[k]}\r\n')

    dirty = True

    while True:
        if dirty:
            cx.echo(cx.term.move_x(0) + led.redraw())
            dirty = False

        ks = None

        while not ks:
            ev = await cx.events.poll('resize', flush=True, get_last=True)

            if ev:
                dirty = True
                cx.echo(f'\r\n{ev}\r\n')
                led.width = cx.term.width - 1
                break
            else:
                ks = await cx.term.inkey(1)

        if ks.code == cx.term.KEY_UP:
            dirty = True
            cx.echo(cx.term.bold_red('\r\nUP!\r\n'))
            cx.echo(f'{await cx.gosub("retval")}\r\n')

        elif ks.code == cx.term.KEY_DOWN:
            dirty = True
            cx.echo(cx.term.bold_red('\r\nDOWN!\r\n'))
            await cx.gosub('down', 1, arg2='adsf')

        elif ks.code == cx.term.KEY_ESCAPE:
            dirty = True
            cx.echo(cx.term.bold_red('\r\nESCAPE!\r\n'))

            return

        elif ks.code == cx.term.KEY_ENTER:
            dirty = True
            cx.echo(f'\r\n{led.value[0]}\r\n')

        else:
            cx.echo(led.process_keystroke(ks))
