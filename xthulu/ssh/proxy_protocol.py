"""
Proxy protocol v1 support

Credit to Ron Frederick <ronf@timeheart.net> for the majority of this code.
"""

# stdlib
import asyncio as aio


class ProxyProtocolSession:

    """Session implementing the PROXY protocol v1"""

    def __init__(self, conn_factory):
        self._conn_factory = conn_factory
        self._conn = None
        self._peername = None
        self._transport: aio.Transport | None = None
        self._inpbuf = []

    def connection_made(self, transport):
        """Connected."""

        self._transport = transport

    def connection_lost(self, exc):
        """Disconnected."""

        if self._conn:
            self._conn.connection_lost(exc)

        self.close()

    def get_extra_info(self, name, default=None):
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
                self._conn.connection_made(self)

                if data:
                    self._conn.data_received(data)
            else:
                self._inpbuf.append(data)

    def eof_received(self):
        """End of file."""

        if self._conn:
            self._conn.eof_received()

    def write(self, data):
        """Write data to the transport (if any)."""

        if self._transport:
            self._transport.write(data)

    def is_closing(self):
        """Notify transport is closing."""

        assert self._transport is not None

        return self._transport.is_closing()

    def abort(self):
        """Abort."""

        self.close()

    def close(self):
        """Close transport."""

        if self._transport:
            self._transport.close()


class ProxyProtocolListener:

    """Tunnel listener which parses PROXY protocol v1 headers"""

    async def create_server(self, conn_factory, listen_host, listen_port):
        """Create the server."""

        def tunnel_factory():
            return ProxyProtocolSession(conn_factory)

        return await aio.get_event_loop().create_server(
            tunnel_factory, listen_host, listen_port  # type: ignore
        )
