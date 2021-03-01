"Userland entry point"

# local
from xthulu.ui import show_art


async def main(cx):
    if cx.encoding == 'utf-8':
        cx.echo('\x1b%G')
    else:
        cx.echo('\x1b%@\x1b(U')

    cx.echo(f'{cx.term.normal}\r\nConnected: '
            f'{cx.term.bold_blue(cx.user.name)}@'
            f'{cx.term.bold_blue(cx.ip)}\r\n')

    await show_art(cx, 'userland/artwork/login.ans')
    await cx.gosub('oneliners')
