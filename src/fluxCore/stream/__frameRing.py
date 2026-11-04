# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, List, Optional, Tuple

# ==================================================================================
from .__eDecodeFormat import DECODEFORMAT
from .__frameHeader import FrameFlags, FrameHeader
from .__streamHelpers import (
    C_DEFAULT_RING_SIZE,
    pickWriteIndex,
    validateRingSize,
)


# ==================================================================================
class FrameRing:
    def __init__(self, size: int = C_DEFAULT_RING_SIZE) -> None:
        size = validateRingSize(size)
        self._size: int = size
        self._slots: List[Tuple[FrameHeader, DECODEFORMAT]] = [None] * size

        self._displayIndex: int = 0        
        self._currentSequence: int = 0

    def publish(self, header: FrameHeader, payload: DECODEFORMAT):
        slots: List[Tuple[FrameHeader, DECODEFORMAT]] = self._slots
        sequence: int = max(self._currentSequence, header.sequence)
        displayIndex: int = self._displayIndex

        oldestSequence: int = min([
            hdr.sequence for hdr, _ in self._slots 
            if hdr is not None and hdr.sequence != sequence]
        )

        writeIdx: int = 0
        for i, (hdr, _) in enumerate(slots):
            if hdr is None:
                writeIdx = i
                break

            else:
                if hdr.sequence == oldestSequence:                    
                    writeIdx = i if i != displayIndex else 0 if displayIndex == self._size - 1 else displayIndex + 1
                    break                        

        self._slots[writeIdx] = (header, payload)
        self._currentSequence = sequence        

    def acquireForDisplay(self) -> Optional[Tuple[FrameHeader, DECODEFORMAT]]:        
        displayIndex: int = self._displayIndex        
        return self._slots[displayIndex]

    def latest(self) -> Optional[Tuple[FrameHeader, DECODEFORMAT]]:
        bestHdr: Optional[FrameHeader] = None        
        for i in range(self._size):
            if i == self._displayIndex: continue
            
            hdr, payload = self._slots[i]
            if hdr is None: continue

            if bestHdr is None or hdr.sequence > bestHdr.sequence:
                bestHdr = hdr

        if bestHdr is None: 
            return None, None

        return bestHdr, payload

    @property
    def size(self) -> int:
        return self._size

# ==================================================================================
__all__ = ["FrameRing"]
# ==================================================================================
