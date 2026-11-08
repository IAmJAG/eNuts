# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Queue, Task, create_task, to_thread
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
C_GROW_STEP: int = 4
C_GROW_MAX: int = 256
C_GROW_WINDOW_NS: int = 1_000_000_000
C_DECODE_QUEUE_SIZE: int = 64
C_STOP_TOKEN: object = object()


# ==================================================================================
class FrameRing:
    """Bounded, serial decoder feeding a zero-copy latest-frame ring.

    Packet submission applies backpressure when the decode queue is full; it
    never drops arbitrary inter-frame packets and therefore preserves codec
    dependency order. Consumers acquire a RingSlot lease through latest() and
    must return it with release() after using its payload.
    """

    def __init__(self, size: int = C_DEFAULT_RING_SIZE, maxGrow: int = C_GROW_MAX) -> None:
        self._size: int = validateRingSize(size)
        self._canGrow: bool = maxGrow >= 0
        self._slots: List[RingSlot] = [RingSlot() for _ in range(self._size)]
        self._queue: Queue = Queue(maxsize=C_DECODE_QUEUE_SIZE)
        self._worker: Optional[Task] = None
        self._running: bool = False
        self._lastGrowNs: int = 0
        self._consecutiveGrows: int = 0

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

    async def _decodeLoop(self) -> None:
        while True:
            item = await self._queue.get()
            try:
                if item is C_STOP_TOKEN:
                    return
                packet, decoder = item
                try:
                    frame: DECODEFORMAT = await to_thread(packet.decode, decoder)
                    if frame is not None:
                        self._publishFrame(
                            frame=frame,
                            sequence=packet.createdAt,
                            pts=packet.pts,
                            width=packet.width,
                            height=packet.height,
                        )
                except Exception as ex:
                    warning(f"[FrameRing] decode failed pts={getattr(packet, 'pts', None)}: {ex}")
            finally:
                self._queue.task_done()

    def _publishFrame(self, frame: DECODEFORMAT, sequence: int, pts: int, width: int, height: int,) -> None:
        idx = self._pickWriteIndex()
        if idx is None:
            if not self._tryGrow():
                warning("[FrameRing] no writable slot; decoded frame skipped")
                return
            idx = self._pickWriteIndex()
            if idx is None:
                warning("[FrameRing] growth produced no writable slot")
                return

        slot = self._slots[idx]
        slot.beginWrite(sequence=sequence, pts=pts, width=width, height=height)
        slot.completeWrite(frame, width=width, height=height, pts=pts)

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

        oldestIdx: Optional[int] = None
        oldestSeq: Optional[int] = None
        for idx, slot in enumerate(self._slots):
            if slot.state is not eSlotFlag.FILLED or slot.readers:
                continue
            if oldestSeq is None or slot.sequence < oldestSeq:
                oldestSeq = slot.sequence
                oldestIdx = idx
        return oldestIdx

    def _tryGrow(self) -> bool:
        if not self._canGrow or self._size >= C_GROW_MAX:
            return False
        now = monotonic_ns()
        if self._lastGrowNs and now - self._lastGrowNs < C_GROW_WINDOW_NS:
            self._consecutiveGrows += 1
            if self._consecutiveGrows == 1:
                warning("FrameRing: consecutive growth (warning)")
            elif self._consecutiveGrows >= 2:
                error("FrameRing: consecutive growth (error) — refusing grow")
                return False
        else:
            self._consecutiveGrows = 0
        step = min(C_GROW_STEP, C_GROW_MAX - self._size)
        if step <= 0:
            return False
        self._slots.extend(RingSlot() for _ in range(step))
        self._size += step
        self._lastGrowNs = now
        verbose(f"FrameRing: grew by {step} → size={self._size}")
        return True

    @property
    def size(self) -> int:
        return self._size

    @property
    def pending(self) -> int:
        return self._queue.qsize()


# ==================================================================================
__all__ = ["FrameRing"]
# ==================================================================================
