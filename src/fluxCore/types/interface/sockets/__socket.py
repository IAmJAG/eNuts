# ==================================================================================
# src/fluxCore/types/interface/sockets/__socket.py
# ==================================================================================
# ==================================================================================
from socket import socket
from typing import Protocol, runtime_checkable


# ==================================================================================
@runtime_checkable
class iSocket(Protocol):
    def __init__(self, sckt: socket): ...
    def receive(self, numBytes: int) -> bytes: ...
    def send(self, payload: bytes) -> None: ...
    def close(self): ...
