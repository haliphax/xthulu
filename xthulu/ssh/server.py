"""SSH server implementation"""

# stdlib
from logging import DEBUG
from secrets import compare_digest

# 3rd party
from asyncssh import SSHServer as AsyncSSHServer, SSHServerConnection
from sqlmodel import func, select

# local
from .. import locks
from ..configuration import get_config
from ..events import EventQueues
from ..logger import log
from ..models import User
from ..resources import db_session


class SSHServer(AsyncSSHServer):
    """xthulu SSH Server"""

    _username: str | None = None
    _peername: list[str]

    _debug_enabled: bool
    _no_password: list[str]
    _no_entry: list[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._debug_enabled = log.getEffectiveLevel() == DEBUG
        self._no_entry = get_config("ssh.auth.bad_usernames", [])
        self._no_password = get_config("ssh.auth.no_password", [])

    @property
    def whoami(self):
        """The peer name in the format username@host"""

        return f"{self._username}@{self._sid}"

    def connection_made(self, conn: SSHServerConnection):
        """
        Connection opened.

        Args:
            conn: The connection object.
        """

        self._peername = conn.get_extra_info("peername")
        self._sid = "{}:{}".format(*self._peername)
        log.info(f"{self._sid} connecting")

    def connection_lost(self, exc: Exception | None):
        """
        Connection lost.

        Args:
            exc: The exception that caused the connection loss, if any.
        """

        if self._sid in EventQueues.q.keys():
            del EventQueues.q[self._sid]

        locks.expire(self._sid)

        if exc:
            log.exception("Subprocess error", exc_info=exc)

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
        auth_required = True

        if username in self._no_password:
            log.info(f"{self.whoami} connected (no password)")
            auth_required = False
        else:
            log.info(f"{self.whoami} authenticating")

        return auth_required

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

        lowered = username.lower()

        if lowered in self._no_entry:
            log.warning(f"{self.whoami} rejected")

            return False

        async with db_session() as db:
            u = (
                await db.exec(
                    select(User).where(func.lower(User.name) == lowered)
                )
            ).one()

        if u is None:
            log.warning(f"{self.whoami} no such user")

            return False

        expected, _ = User.hash_password(password, u.salt)
        assert u.password

        if not compare_digest(expected, u.password):
            log.warning(f"{self.whoami} failed authentication (password)")

            return False

        log.info(f"{self.whoami} authenticated (password)")

        return True
