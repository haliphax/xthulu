"xthulu gosub example"

async def main(xc, arg1, arg2):
    xc.echo('gosub example {} {}\r\n'.format(arg1, arg2))

    with xc.lock('testing') as l:
        if not l:
            xc.echo('Unable to acquire lock\r\n')
        else:
            xc.echo('Got lock\r\n')
            await xc.term.inkey()
            xc.echo('Released\r\n')
