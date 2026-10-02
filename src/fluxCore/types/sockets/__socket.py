# ==================================================================================
# src/fluxCore/types/interface/sockets/__asyncSocket.py
# ==================================================================================
from socket import socket

# ==================================================================================
from ..interface.sockets import iSocket


# ==================================================================================
class SocketBase(iSocket):
    def __init__(self, sckt: socket) -> None:
        sckt.setblocking(False)
        self._socket: socket = sckt

    def close(self):
        self._socket.close()

    def receive(self, numBytes: int) -> bytes: 
        sckt: socket = self._socket
        return sckt.recv(numBytes)
    
    def send(self, payload: bytes):
        sckt: socket = self._socket
        sckt.sendall(payload)
    