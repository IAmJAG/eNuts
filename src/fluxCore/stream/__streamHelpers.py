# ==================================================================================
from __future__ import annotations

from typing import Any, Optional

# ==================================================================================
from .__frameHeader import FrameFlags, FrameHeader

# ==================================================================================
C_DEFAULT_RING_SIZE: int = 2
C_RING_SIZES: list[int] = [2, 4, 8, 16, 32, 64, 128, 256]
C_MIN_RING_SIZE: int = 2

def validateRingSize(size: int) -> int:
    if size < C_MIN_RING_SIZE: return C_DEFAULT_RING_SIZE
    if size in C_RING_SIZES: return size
    nearestSize = min(C_RING_SIZES, key=lambda val: abs(val - size))
    return nearestSize

def pickWriteIndex(displayIndex: int, ringSize: int) -> int:
    candidates = [i for i in range(ringSize) if i != displayIndex]
    return candidates[0] if candidates else 0

def shouldSkipPresent(slotSeq: int, lastPresentedSeq: Optional[int]) -> bool:
    if lastPresentedSeq is None: return False
    return int(slotSeq) == int(lastPresentedSeq)


def makeFrameSlotHeader(
    seq: int,
    pts: int,
    width: int,
    height: int,
    stride: int | None = None,
    format: Any = None,
    flags: FrameFlags = FrameFlags.NONE,
    payload: Any = None,
) -> FrameHeader:
    if stride is None:
        stride = max(0, int(width)) * 4
    return FrameHeader(seq, pts, width, height, stride, format, flags, payload)


__all__ = [
    "C_DEFAULT_RING_SIZE",
    "C_MIN_RING_SIZE",
    "validateRingSize",
    "pickWriteIndex",
    "shouldSkipPresent",
    "makeFrameSlotHeader",
]