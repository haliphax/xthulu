"xthulu lock example"

# api
from xthulu.context import Context


async def main(cx: Context):
    with cx.lock('testing') as l:
        if not l:
            cx.echo('Unable to acquire lock\r\n')
        else:
            cx.echo('Got lock\r\n')
            await cx.term.inkey()
            cx.echo('Released\r\n')
