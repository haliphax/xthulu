"""Choice script helper function"""

# stdlib
from typing import Sequence

# 3rd party
from rich.control import Control

# local
from ..context import SSHContext


async def choice(
    cx: SSHContext,
    prompt: str,
    options: Sequence[str],
    color: str = "black on green",
) -> str:
    """
    Choose from a short list of provided options.

    Args:
        cx: The current SSH context
        prompt: The prompt text to show before the options
        options: A sequence of options, ideally with unique first characters
        color: The color to use for the highlighted option

    Returns:
        The selected option's value
    """

    def _prompt():
        cx.console.control(Control.move_to_column(0))
        cx.echo(prompt)

        for i, option in enumerate(options):
            if opt == i:
                cx.echo(f"[{color}] {option} [/]")
            else:
                cx.echo(f" {option} ")

    cx.console.control(Control.show_cursor(False))
    opt = 0
    how_many = len(options)

    while True:
        _prompt()

        k = await cx.inkey()
        assert k

        if k == b"\x1b[D":
            opt = (opt - 1) if opt > 0 else (how_many - 1)
        elif k in (b"\x1b[C", b"\t"):
            opt = (opt + 1) if opt < (how_many - 1) else 0
        elif k == b"\r":
            break
        else:
            decoded = k.decode()

            for i, key in enumerate([name[0].lower() for name in options]):
                if key == decoded:
                    opt = i
                    break
            else:
                continue

            _prompt()
            break

    cx.console.control(Control.show_cursor(True))

    return options[opt]
