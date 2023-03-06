"""Oneliners script"""

# api
from xthulu.ssh.context import SSHContext
from xthulu.ssh.ui.editors import LineEditor

# local
from userland.handle_events import handle_events
from userland.models import Oneliner

LIMIT = 200
"""Total number of oneliners to keep"""

DISPLAY_LIMIT = 10
"""Number of oneliners to display on screen"""


async def main(cx: SSHContext):
    async def get_oneliners():
        recent = (
            Oneliner.select("id")
            .order_by(Oneliner.id.desc())
            .limit(LIMIT)
            .alias("recent")
            .select()
        )
        oneliners = await Oneliner.query.where(
            Oneliner.id.in_(recent)
        ).gino.all()
        count = len(oneliners)
        offset = max(0, count - DISPLAY_LIMIT)

        return oneliners, count, offset

    def display_oneliners():
        for ol in oneliners[offset : offset + DISPLAY_LIMIT]:
            cx.echo(
                cx.term.clear_eol(),
                cx.term.move_x(0),
                ol.message[: cx.term.width - 1],
                "\r\n",
            )

    def done():
        cx.echo("\r\n")

    banner = (cx.term.bright_white_on_cyan_underline(" Oneliners "), "\r\n\r\n")
    cx.echo(*("\r\n", *banner))
    oneliners, count, offset = await get_oneliners()
    first = True
    editor = LineEditor(cx.term, cx.term.width - 1, limit=79)

    while True:
        if not first:
            cx.echo(cx.term.move_x(0))
            up = max(0, min(count - 1, DISPLAY_LIMIT))

            if up > 0:
                cx.echo(cx.term.move_up(up))

        display_oneliners()
        first = False
        dirty = True

        while True:
            if dirty:
                cx.echo(cx.term.move_x(0) + editor.redraw())
                dirty = False

            ks = None

            while not ks:
                _, dirty = handle_events(cx)

                if dirty:
                    editor.columns = cx.term.width - 1
                    editor.cursor[0] = min(editor.cursor[0], editor.columns)
                    cx.echo(*(cx.term.clear(), *banner))
                    display_oneliners()

                    break

                ks = await cx.term.inkey(1)

            if ks is None:
                continue

            if ks.code == cx.term.KEY_UP:
                last = offset
                offset = max(0, offset - 1)

                if last > 0 and last != offset:
                    break

                continue

            if ks.code == cx.term.KEY_DOWN:
                last = offset
                offset = min(count - DISPLAY_LIMIT, offset + 1)

                if count > DISPLAY_LIMIT and last != offset:
                    break

                continue

            if ks.code == cx.term.KEY_ESCAPE:
                return done()

            if ks.code == cx.term.KEY_ENTER:
                val = editor.value[0].strip()

                if len(val) == 0:
                    return done()

                await Oneliner.create(user_id=cx.user.id, message=val)
                oneliners, count, offset = await get_oneliners()
                editor.reset()

                break

            cx.echo(editor.process_keystroke(ks))
