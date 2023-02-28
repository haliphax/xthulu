"""SSH server implementation"""

# stdlib
from asyncio import Queue

# 3rd party
from asyncssh import (
    SSHServer as AsyncSSHServer,
    SSHServerConnection,
)
from sqlalchemy import func

# local
from .. import locks
from ..configuration import get_config
from ..events import EventQueues
from ..logger import log
from ..models import User


class SSHServer(AsyncSSHServer):

    """xthulu SSH Server"""

    _username: str | None = None
    _peername: list[str]

    @property
    def whoami(self):
        """The peer name in the format username@host"""

        return f"{self._username}@{self._peername[0]}"

    def connection_made(self, conn: SSHServerConnection):
        """
        Connection opened.

        Args:
            conn: The connection object.
        """

        self._peername = conn.get_extra_info("peername")
        self._sid = "{}:{}".format(*self._peername)
        EventQueues.q[self._sid] = Queue()
        log.info(f"{self._peername[0]} connecting")

    def connection_lost(self, exc: Exception):
        """
        Connection lost.

        Args:
            exc: The exception that caused the connection loss, if any.
        """

        del EventQueues.q[self._sid]
        locks.expire(self._sid)

        if exc:
            if bool(get_config("debug.enabled", False)):
                log.error(exc, stack_info=True, stacklevel=10)
            else:
                log.error(exc)

        log.info(f"{self.whoami} disconnected")

    def begin_auth(self, username: str) -> bool:
        """
        Check for auth bypass.

        Args:
            username: The username to check.

        Returns:
            Whether authentication is necessary.
        """

        self._username = username
        pwd_required = True

        if "no_password" in get_config("ssh.auth") and username in get_config(
            "ssh.auth.no_password"
        ):
            log.info(f"{self.whoami} connected (no password)")
            pwd_required = False
        else:
            log.info(f"{self.whoami} authenticating")

        return pwd_required

    def password_auth_supported(self) -> bool:
        """
        Support password authentication.

        Returns:
            True, as this server supports password authentication.
        """

        return True

    async def validate_password(self, username: str, password: str) -> bool:
        """
        Validate provided password.

        Args:
            username: The username to validate.
            password: The password to validate.

        Returns:
            Whether the authentication is valid.
        """

        u = await User.query.where(
            func.lower(User.name) == username.lower()
        ).gino.first()

        if u is None:
            log.warn(f"f{self.whoami} no such user")

            return False

        expected, _ = User.hash_password(password, u.salt)

        if expected != u.password:
            log.warn(f"{self.whoami} failed authentication (password)")

            return False

        log.info(f"{self.whoami} authenticated (password)")

        return True
