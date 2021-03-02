"oneliners script"

# api
from xthulu.context import Context
from xthulu.ui.editors import LineEditor
# local
from userland.models import Oneliner

LIMIT = 200
DISPLAY_LIMIT = 10

async def main(cx: Context):

    async def get_oneliners():
        recent = (Oneliner.select('id').order_by(Oneliner.id.desc())
                  .limit(LIMIT).alias('recent').select())
        oneliners = await (Oneliner.query.where(Oneliner.id.in_(recent))
                           .gino.all())
        count = len(oneliners)
        offset = max(0, count - DISPLAY_LIMIT)

        return oneliners, count, offset

    def done():
        cx.echo('\r\n')

    oneliners, count, offset = await get_oneliners()
    first = True
    led = LineEditor(cx.term, min(78, cx.term.width - 1), limit=78)

    while True:
        if not first:
            cx.echo(cx.term.move_x(0))
            up = max(0, min(count - 1, DISPLAY_LIMIT))

            if up > 0:
                cx.echo(cx.term.move_up(up))

        first = False

        for ol in oneliners[offset:offset + DISPLAY_LIMIT]:
            cx.echo(''.join((
                cx.term.clear_eol(),
                cx.term.move_x(0),
                ol.message[:cx.term.width - 1],
                '\r\n',
            )))

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

            if ks.code == cx.term.KEY_UP:
                last = offset
                offset = max(0, offset - 1)

                if last > 0 and last != offset:
                    break

                continue

            elif ks.code == cx.term.KEY_DOWN:
                last = offset
                offset = min(count - DISPLAY_LIMIT, offset + 1)

                if count > DISPLAY_LIMIT and last != offset:
                    break

                continue

            elif ks.code == cx.term.KEY_ESCAPE:
                return done()

            elif ks.code == cx.term.KEY_ENTER:
                val = led.value[0].strip()

                if len(val) == 0:
                    return done()

                await Oneliner.create(user_id=cx.user.id, message=val)
                oneliners, count, offset = await get_oneliners()
                led.reset()

                break

            else:
                cx.echo(led.process_keystroke(ks))
