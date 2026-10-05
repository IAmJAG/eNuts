# ==================================================================================
from asyncio import AbstractEventLoop
from socket import socket

# ==================================================================================
C_RECV_CHUNK: int = 65535

# ==================================================================================
def ReadExact(sckt: socket, numBytes: int) -> bytes:
    lData = bytearray()
    while len(lData) < numBytes:
        lChunk = sckt.recv(numBytes - len(lData))
        if not lChunk:
            raise ConnectionError("Socket disconnected before exact data received")
        lData.extend(lChunk)
    return bytes(lData)

async def AsyncReadExact(
    sckt: socket, numBytes: int, loop: AbstractEventLoop
) -> bytes:
    lData = bytearray()
    while len(lData) < numBytes:
        lChunk = await loop.sock_recv(sckt, numBytes - len(lData))
        if not lChunk:
            raise ConnectionError("Socket disconnected before exact data received")
        lData.extend(lChunk)
    return bytes(lData)

def ReadAll(sckt: socket, maxBytes: int | None = None) -> bytes:
    lData = bytearray()
    while True:
        lChunk = sckt.recv(C_RECV_CHUNK)
        if not lChunk:
            break
        lData.extend(lChunk)
        if maxBytes is not None and len(lData) > maxBytes:
            raise ValueError(f"Read exceeded maxBytes={maxBytes}")
    return bytes(lData)

async def AsyncReadAll(
    sckt: socket, loop: AbstractEventLoop, maxBytes: int | None = None
) -> bytes:
    lData = bytearray()
    while True:
        lChunk = await loop.sock_recv(sckt, C_RECV_CHUNK)
        if not lChunk:
            break
        lData.extend(lChunk)
        if maxBytes is not None and len(lData) > maxBytes:
            raise ValueError(f"Read exceeded maxBytes={maxBytes}")
    return bytes(lData)
