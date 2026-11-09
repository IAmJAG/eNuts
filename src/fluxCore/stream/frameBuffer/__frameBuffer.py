# ==================================================================================
from __future__ import annotations

# ==================================================================================
from math import ceil
from typing import Dict, List, Optional

# ==================================================================================
from jAGFx.dependencyInjection import Provider
from jAGFx.types.interface.configuration import iConfiguration

# ==================================================================================
from ...types import DECODEFORMAT
from ..__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize
from .__bufferSlot import BufferSlot
from .__frameBufferConfiguration import FrameBufferConfiguration


# ==================================================================================
class FrameBuffer:
    """Multi-consumer zero-copy frame buffer with single next() access point."""
    CFG_SECTION_PATH: str = "fluxCore.stream.frameBuffer"
    def __init__(self, size: int = C_DEFAULT_RING_SIZE, cfg: Optional[FrameBufferConfiguration] = None) -> None:

        if cfg is None:
            config: iConfiguration = Provider.Resolve(iConfiguration)
            if not config.exist(self.CFG_SECTION_PATH):
                config.addSection(self.CFG_SECTION_PATH, FrameBufferConfiguration())

            cfg: FrameBufferConfiguration = config.getSection(self.CFG_SECTION_PATH)

        size: int = validateRingSize(size)
        cfg.currentSize = size

        self._config: FrameBufferConfiguration = cfg
        self._slots: List[BufferSlot] = [BufferSlot() for _ in range(size)]

    def publish(self, sequence: int, payload: DECODEFORMAT, pts: int, width: int, height: int) -> None:
        if not self._freeSlot():

            if self._canGrow(): 
                self._grow()

            else:
                self._evictOldest()

        newSlot: BufferSlot = BufferSlot(sequence=sequence, payload=payload, pts=pts, width=width, height=height)
        self._slots.append(newSlot)

    def next(self, consumerId: int, sequence: Optional[int] = None, timeout: Optional[float] = None) -> Optional[BufferSlot]:
        timeout = timeout if timeout is not None else self._config.defaultReleaseTimeout
        target: Optional[BufferSlot] = None

        if sequence is None:
            target = self._latest()

        else:
            target = self._adjacentGreater(sequence)

        if target is None or target.payload is None: return None

        target.acquire(consumerId, timeout)
        return target

    def _latest(self) -> Optional[BufferSlot]:
        best: Optional[BufferSlot] = None
        for slot in self._slots:
            if slot.payload is None: continue

            if best is None or slot.sequence > best.sequence:
                best = slot

        return best

    def _adjacentGreater(self, sequence: int) -> Optional[BufferSlot]:
        candidates = [s for s in self._slots if s.payload is not None and s.sequence > sequence]
        if not candidates: return None
        return min(candidates, key=lambda s: s.sequence)

    def _freeSlot(self) -> bool:
        freeSlots: Dict[int, BufferSlot] = dict[int, BufferSlot]()        
        for slot in self._slots:            
            if slot.isFree():
                if slot.payload is None: 
                    freeSlots[-1] = slot
                    break

                freeSlots[slot.sequence] = slot

        if len(freeSlots) == 0: return False # None has been freed

        try:
            seq: int = min(freeSlots.keys())
            freeSlot: BufferSlot = freeSlots[seq]
            freeSlot.release()
            self._slots.remove(freeSlot)
            return True
        
        except Exception:
            error("failed to find free slot")
   
    def _canGrow(self) -> bool:
        return (
            self.size < self._config.bufferSizeMax
            and self._vramUsage() < self._config.vramCap
        )

    def _grow(self) -> None:
        newSize = min(self.size * 2, self._config.bufferSizeMax)

        while len(self._slots) < newSize:
            self._slots.append(BufferSlot())

        self._config.currentSize = len(self._slots)

    def _evictOldest(self) -> None:        
        try:
            oldest: BufferSlot = self._slots[min(self._slots, key=lambda s: s.sequence)]
            oldest.release()
            self._slots.remove(oldest)

        except Exception:
            error("failed to evict oldest slot")

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
        return self._config.currentSize

# ==================================================================================
__all__ = ["FrameBuffer"]
# ==================================================================================
