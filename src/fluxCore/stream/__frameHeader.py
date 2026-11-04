# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List, Optional, Tuple

# ==================================================================================
from .__eDecodeFormat import DECODEFORMAT
from .__frameHeader import FrameHeader
from .__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize


# ==================================================================================
class FrameRing:
    def __init__(self, size: int = C_DEFAULT_RING_SIZE) -> None:
        self._size: int = validateRingSize(size)
        self._slots: List[Optional[Tuple[FrameHeader, DECODEFORMAT]]] = [
            None
        ] * self._size
        self._displayIndex: int = 0

    def publish(self, header: FrameHeader, payload: DECODEFORMAT) -> None:
        writeIdx = self._pickWriteIndex()
        self._slots[writeIdx] = (header, payload)

    def latest(self) -> Optional[Tuple[FrameHeader, DECODEFORMAT]]:
        bestIdx: Optional[int] = None
        bestHdr: Optional[FrameHeader] = None
        bestPayload: Optional[DECODEFORMAT] = None

        # Seed with current display slot when it is valid
        displaySlot = self._slots[self._displayIndex]
        if displaySlot is not None:
            bestIdx = self._displayIndex
            bestHdr, bestPayload = displaySlot

        for i in range(self._size):
            if i == self._displayIndex: continue
            slot = self._slots[i]
            if slot is None: continue
            
            hdr, payload = slot
            if bestHdr is None or hdr.sequence > bestHdr.sequence:
                bestIdx = i
                bestHdr = hdr
                bestPayload = payload

        if bestIdx is None or bestHdr is None:
            return None

        self._displayIndex = bestIdx
        return bestHdr, bestPayload

    def _pickWriteIndex(self) -> int:
        """
        Never returns _displayIndex.
        First empty non-display slot wins immediately.
        Otherwise the non-display slot with the lowest sequence.
        """
        oldestIdx: Optional[int] = None
        oldestSeq: Optional[int] = None

        for i in range(self._size):
            if i == self._displayIndex:
                continue
            slot = self._slots[i]
            if slot is None:
                return i  # empty → take at once
            hdr, _ = slot
            if oldestSeq is None or hdr.sequence < oldestSeq:
                oldestSeq = hdr.sequence
                oldestIdx = i

        if oldestIdx is not None:
            return oldestIdx

        # size == 1 fallback
        return 0

    @property
    def size(self) -> int:
        return self._size


__all__ = ["FrameRing"]
