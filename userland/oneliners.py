"oneliners script"

# api
from xthulu.context import Context
from xthulu.ui.editors import LineEditor
# local
from userland.models import Oneliner


async def main(cx: Context):
    oneliners = await Oneliner.query.gino.all()

    for ol in oneliners:
        cx.echo(f'{ol.message}\r\n')

    led = LineEditor(cx.term, cx.term.width - 1, color='bold_white_on_green')
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
                led.columns = cx.term.width - 1
                break
            else:
                ks = await cx.term.inkey(1)

        if ks.code == cx.term.KEY_ESCAPE:
            return

        elif ks.code == cx.term.KEY_ENTER:
            val = led.value[0].strip()

            if len(val) == 0:
                return

            await Oneliner.create(user_id=cx.user.id, message=val)
            return

        else:
            cx.echo(led.process_keystroke(ks))
