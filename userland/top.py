"Userland entry point"

# local
from xthulu.ui import show_art


async def main(cx):
    if cx.encoding == 'utf-8':
        cx.echo('\x1b%G')
    else:
        cx.echo('\x1b%@\x1b(U')

    cx.echo(cx.term.normal +
            '\r\nConnected: {}@{}\r\n'
            .format(cx.term.bold_blue(cx.user.name),
                    cx.term.bold_blue(cx.ip)))

    for k in cx.env.keys():
        cx.echo(f'{k} = {cx.env[k]}\r\n')

    await show_art(cx, 'userland/artwork/login.ans')
    await cx.gosub('oneliners')
