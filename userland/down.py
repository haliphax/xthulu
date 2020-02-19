"xthulu gosub example"

async def main(cx, arg1, arg2):
    cx.echo('gosub example {} {}\r\n'.format(arg1, arg2))

    with cx.lock('testing') as l:
        if not l:
            cx.echo('Unable to acquire lock\r\n')
        else:
            cx.echo('Got lock\r\n')
            await cx.term.inkey()
            cx.echo('Released\r\n')
