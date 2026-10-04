# ==================================================================================
# src/fluxCore/types/interface/sockets/__socket.py
# ==================================================================================
from asyncio import AbstractEventLoop
from socket import socket
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iSocket(Protocol):
    def __init__(self, sckt: socket, loop: AbstractEventLoop | None = None) -> None: ...
    async def receive(self, numBytes: int) -> bytes: ...
    async def send(self, payload: bytes) -> None: ...
    def close(self) -> None: ...
