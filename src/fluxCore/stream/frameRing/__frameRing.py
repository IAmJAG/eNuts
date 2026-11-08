# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Queue, Task, create_task, to_thread
from math import ceil
from time import monotonic_ns
from typing import List, Optional

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from ...types import DECODEFORMAT, eSlotFlag
from ...types.interface.packets import iImagePacket
from ...types.interface.stream.frameRing.slot import iRingSlot
from ..__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize
from .slot import RingSlot

# ==================================================================================
C_DECODE_QUEUE_SIZE: int = 64
C_EVICT_PERCENT: float = 0.20
C_RING_HIGH_WATERMARK: float = 0.80
C_STOP_TOKEN: object = object()


# ==================================================================================
class FrameRing:
    """Fixed-capacity, serial decoder feeding a zero-copy latest-frame ring."""

    def __init__(self, size: int = C_DEFAULT_RING_SIZE) -> None:
        self._size: int = validateRingSize(size)
        self._slots: List[RingSlot] = [RingSlot() for _ in range(self._size)]
        self._queue: Queue = Queue(maxsize=C_DECODE_QUEUE_SIZE)
        self._worker: Optional[Task] = None
        self._running: bool = False
        self._decodedFrames: int = 0
        self._publishedFrames: int = 0
        self._evictedFrames: int = 0
        self._droppedFrames: int = 0
        self._decodeErrors: int = 0
        self._decodeTimeNs: int = 0
        self._maxDecodeTimeNs: int = 0
        self._maxPending: int = 0

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._queue = Queue(maxsize=C_DECODE_QUEUE_SIZE)
        self._worker = create_task(self._decodeLoop())

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        worker = self._worker
        if worker is None:
            return
        await self._queue.put(C_STOP_TOKEN)
        try:
            await worker
        finally:
            self._worker = None

    async def publish(self, packet: iImagePacket, decoder: VideoCodecContext) -> None:
        if decoder is None:
            raise RuntimeError("FrameRing: decoder is not available")
        if not self._running or self._worker is None:
            self.start()
        await self._queue.put((packet, decoder))
        self._maxPending = max(self._maxPending, self._queue.qsize())

    async def _decodeLoop(self) -> None:
        while True:
            item = await self._queue.get()
            try:
                if item is C_STOP_TOKEN:
                    return
                packet, decoder = item
                decodeStartNs = monotonic_ns()
                try:
                    frame: DECODEFORMAT = await to_thread(packet.decode, decoder)
                    if frame is not None:
                        self._decodedFrames += 1
                        self._publishFrame(frame, packet.createdAt, packet.pts, packet.width, packet.height)
                except Exception as ex:
                    self._decodeErrors += 1
                    warning(f"[FrameRing] decode failed pts={getattr(packet, 'pts', None)}: {ex}")
                finally:
                    decodeTimeNs = monotonic_ns() - decodeStartNs
                    self._decodeTimeNs += decodeTimeNs
                    self._maxDecodeTimeNs = max(self._maxDecodeTimeNs, decodeTimeNs)
            finally:
                self._queue.task_done()

    def _publishFrame(self, frame: DECODEFORMAT, sequence: int, pts: int, width: int, height: int) -> None:
        filledCount = sum(slot.state is eSlotFlag.FILLED for slot in self._slots)
        highWatermark = max(1, ceil(self._size * C_RING_HIGH_WATERMARK))
        if filledCount >= highWatermark:
            self._evictOldest()
        idx = self._pickWriteIndex()
        if idx is None:
            self._evictOldest()
            idx = self._pickWriteIndex()
        if idx is None:
            self._droppedFrames += 1
            warning("[FrameRing] no writable slot; decoded frame skipped")
            return
        slot = self._slots[idx]
        slot.beginWrite(sequence=sequence, pts=pts, width=width, height=height)
        slot.completeWrite(frame, width=width, height=height, pts=pts)
        self._publishedFrames += 1

    def _evictOldest(self) -> int:
        filledSlots = [slot for slot in self._slots if slot.state is eSlotFlag.FILLED]
        if len(filledSlots) <= 1:
            return 0
        newestSequence = max(slot.sequence for slot in filledSlots)
        eligibleSlots = sorted(
            (slot for slot in filledSlots if slot.sequence != newestSequence and slot.readers == 0),
            key=lambda slot: slot.sequence,
        )
        if not eligibleSlots:
            return 0
        targetCount = max(1, ceil(len(filledSlots) * C_EVICT_PERCENT))
        evictedCount = min(targetCount, len(eligibleSlots))
        for slot in eligibleSlots[:evictedCount]:
            slot.markFree()
        self._evictedFrames += evictedCount
        return evictedCount

    def latest(self) -> Optional[iRingSlot]:
        best: Optional[RingSlot] = None
        for slot in self._slots:
            if slot.state is not eSlotFlag.FILLED or slot.payload is None:
                continue
            if best is None or slot.sequence > best.sequence:
                best = slot
        if best is None:
            return None
        best.acquire()
        return best

    def next(self) -> Optional[iRingSlot]:
        """Compatibility alias for latest(); returns a leased slot, not a clone."""
        return self.latest()

    def release(self, slot: iRingSlot) -> None:
        if not isinstance(slot, RingSlot):
            raise TypeError("FrameRing.release expects a RingSlot acquired from this ring")
        if slot not in self._slots:
            raise ValueError("FrameRing.release received a slot owned by another ring")
        slot.release()

    def _pickWriteIndex(self) -> Optional[int]:
        for idx, slot in enumerate(self._slots):
            if slot.isWritable:
                return idx
        return None

    @property
    def size(self) -> int:
        return self._size

    @property
    def pending(self) -> int:
        return self._queue.qsize()

    @property
    def stats(self) -> dict[str, int]:
        """Return a point-in-time snapshot of ring and decoder counters."""
        return {
            "capacity": self._size,
            "filled": sum(slot.state is eSlotFlag.FILLED for slot in self._slots),
            "leased": sum(slot.readers > 0 for slot in self._slots),
            "pending": self._queue.qsize(),
            "maxPending": self._maxPending,
            "decodedFrames": self._decodedFrames,
            "publishedFrames": self._publishedFrames,
            "evictedFrames": self._evictedFrames,
            "droppedFrames": self._droppedFrames,
            "decodeErrors": self._decodeErrors,
            "decodeTimeNs": self._decodeTimeNs,
            "maxDecodeTimeNs": self._maxDecodeTimeNs,
        }


# ==================================================================================
__all__ = ["FrameRing", "C_DECODE_QUEUE_SIZE", "C_EVICT_PERCENT", "C_RING_HIGH_WATERMARK"]
# ==================================================================================
