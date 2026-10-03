# ==================================================================================
# src/fluxCore/types/interface/sockets/__asyncSocket.py
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

    def close(self):
        self._socket.close()

    def receive(self, numBytes: int) -> bytes: 
        sckt: socket = self._socket
        return sckt.recv(numBytes)
    
    def send(self, payload: bytes):
        sckt: socket = self._socket
        sckt.sendall(payload)
    
    async def AsyncReceive(self, numBytes: int) -> bytes:
        return await AsyncReadExact(self._socket, numBytes, self._loop)

    async def AsyncSend(self, payload: bytes) -> None:
        await self._loop.sock_sendall(self._socket, payload)
    