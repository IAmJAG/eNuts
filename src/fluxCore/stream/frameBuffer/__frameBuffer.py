# ==================================================================================
from __future__ import annotations

# ==================================================================================
from math import ceil
from typing import List, Optional

# ==================================================================================
from ...types import DECODEFORMAT
from ..__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize
from .__bufferSlot import BufferSlot
from .__ringSlotConfiguration import RingSlotConfiguration

# ==================================================================================
class FrameBuffer:
    """Multi-consumer zero-copy frame buffer with single next() access point."""

    def __init__(self, size: int = C_DEFAULT_RING_SIZE, config: Optional[RingSlotConfiguration] = None) -> None:
        self._config: RingSlotConfiguration = config or RingSlotConfiguration()
        self._size: int = validateRingSize(size)
        self._slots: List[BufferSlot] = [BufferSlot() for _ in range(self._size)]
        self._published: int = 0

    def publish(self, sequence: int, payload: DECODEFORMAT, pts: int, width: int, height: int) -> None:
        """Write a decoded frame into a free or evicted slot."""
        free = self._findFreeSlot()
        if free is None:
            if self._canGrow():
                self._grow()
                free = self._findFreeSlot()
            else:
                self._evictOldest()
                free = self._findFreeSlot()
        if free is None:
            return
        free.write(sequence, payload, pts, width, height)
        self._published += 1

    def next(self, consumerId: int, sequence: Optional[int] = None, timeout: Optional[float] = None) -> Optional[BufferSlot]:
        """Acquire and return the next or latest BufferSlot for the consumer."""
        timeout = timeout if timeout is not None else self._config.defaultReleaseTimeout
        target: Optional[BufferSlot] = None
        if sequence is None:
            target = self._latest()
        else:
            target = self._adjacentGreater(sequence)
        if target is None or target.payload is None:
            return None
        target.acquire(consumerId, timeout)
        return target

    def _latest(self) -> Optional[BufferSlot]:
        best: Optional[BufferSlot] = None
        for slot in self._slots:
            if slot.payload is None:
                continue
            if best is None or slot.sequence > best.sequence:
                best = slot
        return best

    def _adjacentGreater(self, sequence: int) -> Optional[BufferSlot]:
        candidates = [s for s in self._slots if s.payload is not None and s.sequence > sequence]
        if not candidates:
            return None
        return min(candidates, key=lambda s: s.sequence)

    def _findFreeSlot(self) -> Optional[BufferSlot]:
        for slot in self._slots:
            if slot.isFree and slot.payload is None:
                return slot
        return None

    def _canGrow(self) -> bool:
        return self._size < self._config.bufferSizeMax and self._vramUsage() < self._config.vramCap

    def _grow(self) -> None:
        newSize = min(self._size * 2, self._config.bufferSizeMax)
        while len(self._slots) < newSize:
            self._slots.append(BufferSlot())
        self._size = len(self._slots)

    def _evictOldest(self) -> None:
        filled = [s for s in self._slots if s.payload is not None]
        if not filled:
            return
        oldest = min(filled, key=lambda s: s.sequence)
        oldest.release()

    def _vramUsage(self) -> float:
        try:
            import torch
            if torch.cuda.is_available():
                reserved = torch.cuda.memory_reserved()
                total = torch.cuda.get_device_properties(0).total_memory
                return reserved / total if total else 0.0
        except Exception:
            pass
        return 0.0

    @property
    def size(self) -> int:
        return self._size

    @property
    def published(self) -> int:
        return self._published

# ==================================================================================
__all__ = ["FrameBuffer"]
# ==================================================================================
