"xthulu gosub example"

async def main(cx, arg1, arg2):
    cx.echo(f'gosub example {arg1} {arg2}\r\n')

    with cx.lock('testing') as l:
        if not l:
            cx.echo('Unable to acquire lock\r\n')
        else:
            cx.echo('Got lock\r\n')
            await cx.term.inkey()
            cx.echo('Released\r\n')
