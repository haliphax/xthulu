"""
PROXY protocol v1 support

Credit to Ron Frederick <ronf@timeheart.net> for the majority of this code.
"""

# type checking
from typing import Callable

# stdlib
from asyncio import get_event_loop, Transport

# 3rd party
from asyncssh import SSHServerConnection, SSHServerSession


class ProxyProtocolSession:
    """Session implementing the PROXY protocol v1"""

    def __init__(self, conn_factory: Callable):
        self._conn_factory = conn_factory
        self._conn: SSHServerConnection | None = None
        self._peername: tuple[str, int] | None = None
        self._transport: Transport | None = None
        self._inpbuf: list[bytes] = []

    def connection_made(self, transport: Transport):
        self._transport = transport

    connection_made.__doc__ = SSHServerSession.connection_made.__doc__

    def connection_lost(self, exc: Exception):
        if self._conn:
            self._conn.connection_lost(exc)

        self.close()

    connection_lost.__doc__ = SSHServerSession.connection_lost.__doc__

    def get_extra_info(self, name: str, default=None):
        """Return proxied peername; fallback to transport for other values."""

        assert self._transport is not None

        if name == "peername":
            return self._peername
        else:
            return self._transport.get_extra_info(name, default)

    def data_received(self, data: bytes):
        """Look for PROXY headers during connection establishment."""

        if self._conn:
            self._conn.data_received(data)
        else:
            idx = data.find(b"\r\n")

            if idx >= 0:
                self._inpbuf.append(data[:idx])
                data = data[idx + 2 :]

                conn_info = b"".join(self._inpbuf).split()
                self._inpbuf.clear()

                self._peername = (
                    conn_info[2].decode("ascii"),
                    int(conn_info[4]),
                )
                self._conn = self._conn_factory("", 0)
                self._conn.connection_made(self)  # type: ignore

                if data:
                    self._conn.data_received(data)  # type: ignore
            else:
                self._inpbuf.append(data)

    def eof_received(self):
        if self._conn:
            self._conn.eof_received()

    eof_received.__doc__ = SSHServerSession.eof_received.__doc__

    def write(self, data: bytes):
        if self._transport:
            self._transport.write(data)

    write.__doc__ = Transport.write.__doc__

    def is_closing(self):
        return self._transport.is_closing() if self._transport else None

    is_closing.__doc__ = Transport.is_closing.__doc__

    def abort(self):
        self.close()

    abort.__doc__ = Transport.abort.__doc__

    def close(self):
        return self._transport.close() if self._transport else None

    close.__doc__ = Transport.close.__doc__


class ProxyProtocolListener:
    """Tunnel listener which passes connections to a PROXY protocol session"""

    async def create_server(
        self, conn_factory: Callable, listen_host: str, listen_port: int
    ):
        """
        Create the server.

        Args:
            conn_factory: A callable which will be called and provided with \
                the connection information when a new connection is tunneled.
            listen_host: The hostname to bind.
            listen_port: The port number to bind.

        Returns:
            An asyncio server for tunneling SSH connections.
        """

        def tunnel_factory():
            return ProxyProtocolSession(conn_factory)

        return await get_event_loop().create_server(
            tunnel_factory,  # type: ignore
            listen_host,
            listen_port,  # type: ignore
        )
