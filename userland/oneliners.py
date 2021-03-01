"oneliners script"

# api
from xthulu import db
from xthulu.context import Context
from xthulu.ui.editors import LineEditor
# local
from userland.models import Oneliner

LIMIT = 200

async def main(cx: Context):
    recent = (Oneliner.select('id').order_by(Oneliner.id.desc()).limit(LIMIT)
              .alias('recent').select())
    oneliners = await Oneliner.query.where(Oneliner.id.in_(recent)).gino.all()

    for ol in oneliners:
        cx.echo(f'{ol.message[:cx.term.width - 1]}\r\n')

    led = LineEditor(cx.term, cx.term.width - 1, color='bold_white_on_green',
                     limit=78)
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

            ks = await cx.term.inkey(1)

        if ks.code == cx.term.KEY_ESCAPE:
            break

        elif ks.code == cx.term.KEY_ENTER:
            val = led.value[0].strip()

            if len(val) == 0:
                break

            await Oneliner.create(user_id=cx.user.id, message=val)

            break

        else:
            cx.echo(led.process_keystroke(ks))

    cx.echo('\r\n')
