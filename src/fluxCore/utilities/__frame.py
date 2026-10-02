# ==================================================================================
from asyncio import AbstractEventLoop
from socket import socket

# ==================================================================================
from .__socket import AsyncReadExact, ReadExact

# ==================================================================================
C_MAX_FRAME_BYTES: int = 32 * 1024 * 1024  # 32 MiB ceiling


# ==================================================================================
def _ParseFrameHeader(ptsBytes: bytes, sizeBytes: bytes) -> tuple[int, int]:
    lPts = int.from_bytes(ptsBytes, byteorder="big")
    lSize = int.from_bytes(sizeBytes, byteorder="big")
    if lSize < 0 or lSize > C_MAX_FRAME_BYTES: 
        raise ValueError(f"Invalid frame size {lSize} (max {C_MAX_FRAME_BYTES})")
    return lPts, lSize


def ReadSingleFrame(sckt: socket) -> tuple[int, bytes] | None:
    """
    Returns (pts, payload) or None on clean EOF before a full header.
    Raises ConnectionError / ValueError / OSError on protocol or I/O failure.
    """
    try:
        lPtsBytes = ReadExact(sckt, 8)
        lSizeBytes = ReadExact(sckt, 4)

    except ConnectionError:
        return None

    lPts, lSize = _ParseFrameHeader(lPtsBytes, lSizeBytes)
    lPayload = ReadExact(sckt, lSize)
    return lPts, lPayload

async def AsyncReadSingleFrame(sckt: socket, loop: AbstractEventLoop ) -> tuple[int, bytes] | None:
    """
    Async counterpart of ReadSingleFrame.
    Returns (pts, payload) or None on clean EOF before a full header.
    """
    try:
        lPtsBytes = await AsyncReadExact(sckt, 8, loop)
        lSizeBytes = await AsyncReadExact(sckt, 4, loop)
    except ConnectionError:
        return None

    lPts, lSize = _ParseFrameHeader(lPtsBytes, lSizeBytes)
    lPayload = await AsyncReadExact(sckt, lSize, loop)
    return lPts, lPayload
