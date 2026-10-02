# ==================================================================================
# src/fluxCore/types/interface/sockets/__socket.py
# ==================================================================================
from asyncio import AbstractEventLoop, get_running_loop
from socket import socket

# ==================================================================================
from ..interface.sockets import iSocket


# ==================================================================================
class AsyncSocket(iSocket):
    def __init__(self, sckt: socket, loop: AbstractEventLoop | None = None) -> None:
        sckt.setblocking(False)
        self._socket: socket = sckt
        self._loop: AbstractEventLoop = loop or get_running_loop()

    def close(self):
        self._socket.close()

    def receive(self, numBytes: int) -> bytes: ...
    def send(self, payload: bytes) -> None: ...
    