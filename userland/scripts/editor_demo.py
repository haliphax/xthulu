"""Editor demo script"""

# 3rd party
from blessed.keyboard import Keystroke

# api
from xthulu.ssh.context import SSHContext
from xthulu.ssh.ui.editors import BlockEditor
from xthulu.ssh.terminal.constants import CTRL_C

# local
from userland.handle_events import handle_events


async def main(cx: SSHContext):
    banner = (
        cx.term.bright_white_on_magenta_underline(" Editor demo "),
        "\r\n\r\n",
    )
    cx.echo(*("\r\n\r\n", *banner))

    # demonstration text
    text_to_repeat = [
        "one " * 200,
        "two " * 200,
        "three " * 200,
        "four " * 200,
        "five " * 200,
        "six " * 200,
        "seven " * 200,
        "eight " * 200,
        "",
    ]
    text: list[str] = []

    for _ in range(10):
        for line in text_to_repeat:
            text.append(line.strip())

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
            _, dirty = handle_events(cx)

            if dirty:
                editor.columns = cx.term.width - 1
                editor.cursor[0] = min(editor.cursor[0], editor.columns - 1)
                cx.echo(*(cx.term.clear(), *banner))

                break

            ks = await cx.term.inkey(1)

        if ks is None:
            continue

        if ks.code == cx.term.KEY_ESCAPE or ks == CTRL_C:
            # move cursor after the last row of the editor before exiting
            out = (cx.term.normal, "\r\n" * (editor.rows - editor.cursor[1]))

            return cx.echo(*out)

        cx.echo(editor.process_keystroke(ks))
