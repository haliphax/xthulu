"""Editor demo script"""

# 3rd party
from blessed.keyboard import Keystroke

# api
from xthulu.ssh.context import SSHContext
from xthulu.ssh.ui.editors import BlockEditor


async def main(cx: SSHContext):
    banner = (
        cx.term.bold_white_on_magenta_underline(" Editor demo "),
        "\r\n\r\n",
    )
    cx.echo(*("\r\n\r\n", *banner))

    # demonstration text
    text_to_repeat = [
        "abc" * 200,
        "bcd" * 200,
        "cde" * 200,
        "def" * 200,
        "efg" * 200,
        "fgh" * 200,
        "ghi" * 200,
        "hij" * 200,
    ]
    text: list[str] = []

    for _ in range(10):
        text += text_to_repeat

    editor = BlockEditor(
        term=cx.term,
        rows=10,
        columns=cx.term.width - 1,
        pos=[0, 0],
        cursor=[0, 0],
        value=text,
    )

    # if the editor should be redrawn
    dirty = True

    while True:
        if dirty:
            cx.echo(editor.redraw(anchor=False))
            dirty = False

        ks: Keystroke | None = None

        while not ks:
            ev = await cx.events.poll("resize", flush=True, get_last=True)

            if ev:
                dirty = True
                editor.columns = cx.term.width - 1
                editor.cursor[0] = min(editor.cursor[0], editor.columns - 1)
                cx.echo(*(cx.term.clear(), *banner))

                break

            ks = await cx.term.inkey(1)

        if ks is None:
            continue

        if ks.code == cx.term.KEY_ESCAPE:
            # move cursor after the last row of the editor before exiting
            out = (cx.term.normal, "\r\n" * (editor.rows - editor.cursor[1]))

            return cx.echo(*out)

        cx.echo(editor.process_keystroke(ks))
