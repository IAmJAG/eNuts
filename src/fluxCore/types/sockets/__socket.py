# ==================================================================================
# src/fluxCore/types/sockets/__socket.py
# ==================================================================================
from asyncio import AbstractEventLoop, get_running_loop
from socket import socket

# ==================================================================================
from ...utilities import AsyncReadExact
from ..interface.sockets import iSocket


# ==================================================================================
class SocketBase(iSocket):
    def __init__(self, sckt: socket, loop: AbstractEventLoop | None = None) -> None:
        sckt.setblocking(False)
        self._socket: socket = sckt
        self._loop: AbstractEventLoop = loop or get_running_loop()

    def close(self) -> None:
        self._socket.close()

    async def receive(self, numBytes: int) -> bytes:
        return await AsyncReadExact(self._socket, numBytes, self._loop)

    async def send(self, payload: bytes) -> None:
        await self._loop.sock_sendall(self._socket, payload)
