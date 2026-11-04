# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, List, Optional

# ==================================================================================
from .__frameHeader import FrameFlags, FrameHeader
from .__streamHelpers import (
    C_DEFAULT_RING_SIZE,
    makeFrameSlotHeader,
    pickWriteIndex,
    validateRingSize,
)


# ==================================================================================
class FrameRing:
    def __init__(self, size: int = C_DEFAULT_RING_SIZE) -> None:
        self._size: int = validateRingSize(size)
        self._slots: List[Optional[FrameHeader]] = [None] * self._size        
        self._displayIndex: int = 0
        self._seq: int = 0

    def publish( self, width: int, height: int, pts: int,
        flags: FrameFlags = FrameFlags.NONE,
        payload: Any = None,
    ) -> FrameHeader:
        self._seq += 1
        writeIdx = pickWriteIndex(self._displayIndex, self._size)
        hdr = makeFrameSlotHeader(
            seq=self._seq,
            pts=int(pts),
            width=int(width),
            height=int(height),
            stride=max(0, int(width)) * 4,
            flags=flags,
            payload=payload,
        )
        self._slots[writeIdx] = hdr
        return hdr

    def acquireForDisplay(self) -> Optional[tuple[int, FrameHeader, Any]]:
        """Return (index, header, payload) of the newest ready slot, or None."""
        bestIdx: Optional[int] = None
        bestHdr: Optional[FrameHeader] = None
        for i in range(self._size):
            if i == self._displayIndex:
                continue
            hdr = self._slots[i]
            if hdr is None:
                continue
            if bestHdr is None or hdr.seq > bestHdr.seq:
                bestIdx = i
                bestHdr = hdr
        if bestIdx is None or bestHdr is None:
            return None
        return bestIdx, bestHdr, bestHdr.payload

    def setDisplayIndex(self, idx: int) -> None:
        if 0 <= idx < self._size:
            self._displayIndex = idx

    def latest(self) -> Optional[tuple[FrameHeader, Any]]:
        bestHdr: Optional[FrameHeader] = None
        for i in range(self._size):
            if i == self._displayIndex:
                continue
            hdr = self._slots[i]
            if hdr is None:
                continue
            if bestHdr is None or hdr.seq > bestHdr.seq:
                bestHdr = hdr
        if bestHdr is None:
            return None
        return bestHdr, bestHdr.payload

    @property
    def size(self) -> int:
        return self._size


__all__ = ["FrameRing"]