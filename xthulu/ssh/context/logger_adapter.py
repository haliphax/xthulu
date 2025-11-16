"""Context specific LoggerAdapter implementation"""

# type checking
from typing import Any, Mapping, MutableMapping

# stdlib
from logging import LoggerAdapter


class ContextLoggerAdapter(LoggerAdapter):
    """LoggerAdapter for prepending log messages with connection info"""

    whoami: str | None

    def __init__(
        self, logger: Any, extra: Mapping[str, object] | None = None
    ) -> None:
        super(ContextLoggerAdapter, self).__init__(logger, extra)

        if extra and "whoami" in extra.keys():
            self.whoami = str(extra["whoami"])

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        return f"{self.whoami} {msg}", kwargs
