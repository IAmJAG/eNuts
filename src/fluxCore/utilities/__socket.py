# ==================================================================================
from asyncio import AbstractEventLoop
from socket import socket


# ==================================================================================
async def asyncReadExact(sckt: socket, numBytes: int, loop: AbstractEventLoop) -> bytes:
    data: bytes = b""
    while len(data) < numBytes:
        try:
            chunk = await loop.sock_recv(sckt, numBytes - len(data))
            if not chunk:
                raise ConnectionError(
                    "Video stream is disconnected before data is complete"
                )

            data += chunk

        except Exception as e:
            raise Exception(f"Error during receive: {e}") from e

    return data


async def asyncReadAll(sckt: socket, loop: AbstractEventLoop) -> bytes:
    data: bytes = b""
    while True:
        try:
            chunk = await loop.sock_recv(sckt, 65535)
            if not chunk:
                break
            data += chunk

        except Exception as e:
            raise Exception(f"Error during receive: {e}") from e

    return data


def readExact(socket: socket, numBytes: int) -> bytes:
    data = b""
    while len(data) < numBytes:
        chunk = socket.recv(numBytes - len(data))
        if not chunk:
            raise ConnectionError("Video stream is disconnected")

        data += chunk
    return data


def readAll(socket: socket) -> bytes:
    data = b""
    while True:
        chunk = socket.recv(65535)
        if not chunk:
            break
        data += chunk
    return data


async def asyncReadSingleFrame(lSocket: socket, loop: AbstractEventLoop):
    lPtsBytes = await loop.sock_recv(lSocket, 8)
    if not lPtsBytes:
        return None
    lPts = int.from_bytes(lPtsBytes, byteorder="big")

    lSizeBytes = await loop.sock_recv(lSocket, 4)
    if not lSizeBytes:
        return None

    lActualPacketSize = int.from_bytes(lSizeBytes, byteorder="big")

    lSingleFrameImageBytes = await loop.sock_recv(lSocket, lActualPacketSize)

    return lSingleFrameImageBytes


def readSingleFrame(lSocket: socket):
    lPtsBytes = lSocket.recv(8)
    if not lPtsBytes:
        return None
    lPts = int.from_bytes(lPtsBytes, byteorder="big")

    lSizeBytes = lSocket.recv(4)
    if not lSizeBytes:
        return None

    lActualPacketSize = int.from_bytes(lSizeBytes, byteorder="big")

    lSingleFrameImageBytes = lSocket.recv(lActualPacketSize)

    return lPts, lActualPacketSize, lSingleFrameImageBytes
