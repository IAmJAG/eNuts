# ==================================================================================
from asyncio import AbstractEventLoop
from socket import socket
from struct import unpack

# ==================================================================================
from .__socket import AsyncReadExact, ReadExact

# ==================================================================================
C_MAX_FRAME_BYTES: int = 32 * 1024 * 1024
C_FLAG_CONFIG: int = 0x8000_0000_0000_0000
C_FLAG_KEYFRAME: int = 0x4000_0000_0000_0000
C_PTS_MASK: int = 0x3FFF_FFFF_FFFF_FFFF


# ==================================================================================
def _ParseFrameHeader(header12: bytes) -> tuple[int, bool, bool, int]:
    if len(header12) < 12: raise ConnectionError("Incomplete frame header")
    lHeaderVal, lSize = unpack(">QI", header12)

    if lSize < 0 or lSize > C_MAX_FRAME_BYTES: 
        raise ValueError(f"Invalid frame size {lSize} (max {C_MAX_FRAME_BYTES})")
    
    lIsConfig = (lHeaderVal & C_FLAG_CONFIG) != 0
    lIsKeyFrame = (lHeaderVal & C_FLAG_KEYFRAME) != 0
    lPts = lHeaderVal & C_PTS_MASK
    return lPts, lIsConfig, lIsKeyFrame, lSize

# ==================================================================================
def ReadSingleFrame(sckt: socket) -> tuple[int, bool, bool, bytes] | None:
    try:
        lHeader = ReadExact(sckt, 12)

    except ConnectionError:
        return None
    
    lPts, lIsConfig, lIsKeyFrame, lSize = _ParseFrameHeader(lHeader)
    lPayload = ReadExact(sckt, lSize) if lSize else b""
    return lPts, lIsConfig, lIsKeyFrame, lPayload

async def AsyncReadSingleFrame(sckt: socket, loop: AbstractEventLoop) -> tuple[int, bool, bool, bytes] | None:
    try:
        lHeader = await AsyncReadExact(sckt, 12, loop)

    except ConnectionError:
        return None
    
    lPts, lIsConfig, lIsKeyFrame, lSize = _ParseFrameHeader(lHeader)
    lPayload = await AsyncReadExact(sckt, lSize, loop) if lSize else b""
    return lPts, lIsConfig, lIsKeyFrame, lPayload