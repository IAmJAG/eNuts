# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Task, to_thread
from collections import deque
from time import monotonic_ns
from typing import Dict, List, Optional, Tuple

# ==================================================================================
from av import VideoCodecContext
from torch import Tensor

# ==================================================================================
from ...types import DECODEFORMAT, eTimeDeltaFormat
from ...types.interface.packets import iImagePacket
from ..__frameHeader import FrameHeader
from ..__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize
from .slot import RingSlot, eSlotFlag

# ==================================================================================
# Growth policy
C_GROW_STEP: int = 4
C_GROW_MAX: int = 256
C_GROW_WINDOW_NS: int = 1_000_000_000  # 1s
# ==================================================================================

class FrameRing:
    def __init__(self, size: int = C_DEFAULT_RING_SIZE, maxGrow: int = C_GROW_MAX) -> None:
        self._size: int = validateRingSize(size)
        self._canGrow: bool = maxGrow >= 0
        self._slots: List[RingSlot] = [RingSlot() for _ in range(self._size)]

        # Sequential cursor for recorder (index into publish order)
        self._readSeq: int = 0  # next sequence the recorder expects (by order counter)
        self._writeOrder: int = 0  # monotonic publish counter (not ns)
        self._order: List[int] = []  # slot indices in publish order (for next)

        # Growth guard
        self._lastGrowNs: int = 0
        self._consecutiveGrows: int = 0

    def publish(self, packet: iImagePacket, decoder: VideoCodecContext, imageSize: int = -1) -> None:
        idx = self._pickWriteIndex()
        if idx is None:
            if not self._tryGrow():
                raise RuntimeError("FrameRing: no writable slot and cannot grow")
            idx = self._pickWriteIndex()
            if idx is None:
                raise RuntimeError("FrameRing: grow succeeded but no writable slot")

        slot = self._slots[idx]

        slot.beginWrite(
            sequence=packet.createdAt,  
            pts=packet.pts,
            width=packet.width,
            height=packet.height,
        )
        self._order.append(idx)
        
        createTask(self._decode, idx, slot, packet, decoder, imageSize)


    async def _decode(self, idx: int, slot: RingSlot, packet: iImagePacket, decoder: VideoCodecContext, imageSize: int = -1) -> None:
        try:
            frame: DECODEFORMAT = await to_thread(packet.decode, decoder, imageSize)
            if frame is None:
                self._abandonWrite(idx, slot)
                return

            # width/height may be updated by decode (e.g. TensorPacket resize)
            slot.completeWrite(
                frame,
                width=packet.width,
                height=packet.height,
                pts=packet.pts,
            )

        except Exception as ex:
            self._abandonWrite(idx, slot)
            warning(f"failed idx={idx}: {ex}")
            raise

    def _abandonWrite(self, idx: int, slot: RingSlot) -> None:
        """Decode failed or null frame: drop from order and free slot."""
        try:
            # Remove this idx from order (may not be head if later publishes queued)
            self._order = [i for i in self._order if i != idx]

        except Exception:
            pass

        finally:
            slot.markFree()

    def latest(self) -> Optional[DECODEFORMAT]:
        best = None
        for slot in self._slots:
            if slot.state is not eSlotFlag.FILLED or slot.payload is None:
                continue
            if best is None or slot.sequence > best.sequence:
                best = slot
        if best is None:
            return None

        payload: Tensor = best.payload
        return payload.detach().clone()


    def next(self) -> Optional[DECODEFORMAT]:
        while self._order:
            idx = self._order[0]
            slot = self._slots[idx]            
            
            if slot.state is eSlotFlag.WRITING:
                return None
            
            if slot.state is not eSlotFlag.FILLED or slot.payload is None:
                self._order.pop(0)
                continue

            payload: Tensor = slot.payload
            return payload.detach().clone()
        
        return None

    def release(self, slot: RingSlot) -> None:
        if not self._order: return
        idx = self._order[0]
        if self._slots[idx] is not slot:
            return
        self._order.pop(0)
        slot.markFree()

    def _pickWriteIndex(self) -> Optional[int]:
        freeIdx: Optional[int] = None
        oldestIdx: Optional[int] = None
        oldestSeq: Optional[int] = None

        for i, slot in enumerate(self._slots):
            if slot.state is eSlotFlag.WRITING: continue
            if slot.isWritable: return i

            if i in self._order: continue

            if slot.state is eSlotFlag.FILLED:
                if oldestSeq is None or slot.sequence < oldestSeq:
                    oldestSeq = slot.sequence
                    oldestIdx = i

        if freeIdx is not None: return freeIdx
        return oldestIdx

    def _tryGrow(self) -> bool:
        if not self._canGrow or self._size >= C_GROW_MAX:
            return False

        now = monotonic_ns()
        if self._lastGrowNs and (now - self._lastGrowNs) < C_GROW_WINDOW_NS:
            self._consecutiveGrows += 1
            
            if self._consecutiveGrows == 1:
                warning("FrameRing: consecutive growth (warning)")

            elif self._consecutiveGrows >= 2:
                error("FrameRing: consecutive growth (error) — refusing grow")
                return False
            
        else:
            self._consecutiveGrows = 0

        step = min(C_GROW_STEP, C_GROW_MAX - self._size)
        if step <= 0: return False

        self._slots.extend(RingSlot() for _ in range(step))
        self._size += step
        self._lastGrowNs = now

        verbose(f"FrameRing: grew by {step} → size={self._size}")
        
        return True

    @property
    def size(self) -> int:
        return self._size

# ==================================================================================
__all__ = ["FrameRing"]
# ==================================================================================