"Userland entry point"

# local
from xthulu.ui.editors import LineEditor


async def main(cx):
    if cx.encoding == 'utf-8':
        cx.echo('\x1b%G')
    else:
        cx.echo('\x1b%@\x1b(U')

    cx.echo(cx.term.normal)
    cx.echo(cx.term.move_x(0) + cx.term.clear_eol)
    cx.echo('Connected: {}@{}\r\n'
            .format(cx.term.bold_blue(cx.user.name),
                    cx.term.bold_blue(cx.ip)))

    led = LineEditor(cx.term, cx.term.width - 1, color='bold_white_on_green',
                     value='testing this thing')

    for k in cx.env.keys():
        cx.echo('{} = {}\r\n'.format(k, cx.env[k]))

    dirty = True

    while True:
        if dirty:
            cx.echo(cx.term.move_x(0) + led.redraw())
            dirty = False

        ks = None

        while not ks:
            ev = await cx.events.poll('resize')

            if ev:
                cx.echo(repr(ev) + '\r\n')
                await cx.events.flush('resize')

            ks = await cx.term.inkey(1)

        if ks.code == cx.term.KEY_LEFT:
            dirty = True
            cx.echo(cx.term.bold_red('LEFT!\r\n'))
        elif ks.code == cx.term.KEY_RIGHT:
            dirty = True
            cx.echo(cx.term.bold_red('RIGHT!\r\n'))
        elif ks.code == cx.term.KEY_UP:
            dirty = True
            cx.echo(cx.term.bold_red('UP!\r\n'))
            cx.echo('{}\r\n'.format(await cx.gosub('retval')))
        elif ks.code == cx.term.KEY_DOWN:
            dirty = True
            cx.echo(cx.term.bold_red('DOWN!\r\n'))
            await cx.gosub('down', 1, arg2='adsf')
        elif ks.code == cx.term.KEY_ESCAPE:
            dirty = True
            cx.echo(cx.term.bold_red('ESCAPE!\r\n'))

            return
        else:
            cx.echo(led.process_keystroke(ks))
