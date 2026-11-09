# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Event, Lock, Queue, Task, create_task, to_thread
from math import ceil
from time import monotonic_ns
from typing import Optional

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from jAGFx.dependencyInjection import Provider
from jAGFx.logging import warning
from jAGFx.types.interface.configuration import iConfiguration

# ==================================================================================
from ...configurations import FrameRingConfiguration
from ...types import DECODEFORMAT, eSlotFlag
from ...types.interface.packets import iImagePacket
from ...types.interface.stream.frameRing.slot import iRingSlot
from ..__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize
from .slot import RingSlot

# ==================================================================================
C_DECODE_QUEUE_MINIMUM: int = 4
C_DECODE_QUEUE_MAXIMUM: int = 256
C_DECODE_QUEUE_SIZE: int = C_DECODE_QUEUE_MINIMUM
C_EVICT_PERCENT: float = 0.20
C_RING_HIGH_WATERMARK: float = 0.80
C_STOP_TOKEN: object = object()


# ==================================================================================
class FrameRing:
    CFG_SECTION_PATH: str = "fluxCore.stream.frameRing"

    def __init__(self, size: int = C_DEFAULT_RING_SIZE) -> None:
        cfg: iConfiguration = Provider.Resolve(iConfiguration)
        if not cfg.exist(self.CFG_SECTION_PATH):
            cfg.addSection(self.CFG_SECTION_PATH, FrameRingConfiguration())

        cfg: FrameRingConfiguration = cfg.getSection(self.CFG_SECTION_PATH)
        self._config: FrameRingConfiguration = cfg

        self._size: int = validateRingSize(size)
        self._slots: list[RingSlot] = [RingSlot() for _ in range(self._size)]
        self._queue: Queue[object] = Queue(maxsize=cfg.decodeCapacity.maximum)
        self._decodeQueueLimit: int = cfg.decodeCapacity.current

        self._worker: Optional[Task[None]] = None
        self._running: bool = False
        self._stopping: bool = False
        self._accepting: bool = False
        self._decoder: Optional[VideoCodecContext] = None

        self._publishLock: Lock = Lock()
        self._defaultSequenceLock: Lock = Lock()
        self._slotChanged: Event = Event()
        self._currentSequence: Optional[int] = None
        self._lastCreatedAt: Optional[int] = None

        self._decodedFrames: int = 0
        self._publishedFrames: int = 0
        self._evictedFrames: int = 0
        self._droppedFrames: int = 0
        self._invalidTimestampPackets: int = 0
        self._decodeErrors: int = 0
        self._decodeTimeNs: int = 0
        self._maxDecodeTimeNs: int = 0
        self._maxPending: int = 0

    # ==================================================================================
    def setDecoder(self, decoder: VideoCodecContext) -> None:
        self._decoder = decoder

    # ==================================================================================
    def start(self) -> None:
        if self._running:
            return

        self._stopping = False
        self._accepting = True
        self._running = True
        self._worker = create_task(self._decodeLoop())

    # ==================================================================================
    async def stop(self) -> None:
        if not self._running:
            return

        self._accepting = False
        self._stopping = True
        self._slotChanged.set()

        await self._queue.join()
        await self._queue.put(C_STOP_TOKEN)

        worker: Optional[Task[None]] = self._worker
        if worker is not None:
            try:
                await worker
            finally:
                self._worker = None

        self._running = False
        self._stopping = False
        self._slotChanged.set()

    # ==================================================================================
    async def publish(
        self,
        packet: iImagePacket,
        decoder: Optional[VideoCodecContext] = None,
    ) -> None:
        if decoder is not None:
            self._decoder = decoder

        if self._decoder is None:
            raise RuntimeError("FrameRing decoder is not available")

        if not self._running: self.start()

        if not self._accepting:
            self._droppedFrames += 1
            return

        createdAt: int = int(packet.createdAt)
        async with self._publishLock:
            if self._lastCreatedAt is not None and createdAt <= self._lastCreatedAt:
                self._invalidTimestampPackets += 1
                warning(
                    f"Skipping packet with non-increasing createdAt timestamp: "
                    f"createdAt={createdAt}, lastCreatedAt={self._lastCreatedAt}"
                )
                return

            vramUtilization: Optional[float] = self._getVramUtilization()
            if vramUtilization is not None and vramUtilization > self._config.vramCap:
                self._evictOldest()
                self._releaseCachedVram()
                vramUtilization = self._getVramUtilization()
                if vramUtilization is not None and vramUtilization > self._config.vramCap:
                    self._droppedFrames += 1
                    warning(
                        "Skipping packet because device memory utilization exceeds "
                        f"the configured {self._config.vramCap:.0%} VRAM cap"
                    )
                    return

            if self._queue.qsize() >= self._decodeQueueLimit:
                if self._decodeQueueLimit < self._config.decodeCapacity.maximum:
                    self._decodeQueueLimit = min(
                        self._config.decodeCapacity.maximum,
                        max(self._decodeQueueLimit + 1, self._decodeQueueLimit * 2),
                    )
                    self._config.decodeCapacity.current = self._decodeQueueLimit
                elif vramUtilization is not None and vramUtilization > self._config.vramCap:
                    self._droppedFrames += 1
                    warning("Skipping packet because decode queue cannot grow under VRAM pressure")
                    return

            await self._queue.put(packet)
            self._lastCreatedAt = createdAt
            self._maxPending = max(self._maxPending, self._queue.qsize())

    # ==================================================================================
    async def _decodeLoop(self) -> None:
        while True:
            packet: object = await self._queue.get()
            try:
                if packet is C_STOP_TOKEN:
                    return

                self._shrinkDecodeQueueLimit()
                imagePacket: iImagePacket = packet
                decoder: Optional[VideoCodecContext] = self._decoder
                if decoder is None:
                    self._decodeErrors += 1
                    warning("FrameRing decode skipped because decoder is unavailable")
                    continue

                decodeStartNs: int = monotonic_ns()
                try:
                    frame: DECODEFORMAT = await to_thread(imagePacket.decode, decoder)
                    if frame is not None:
                        self._decodedFrames += 1
                        await self._publishFrame(
                            frame,
                            int(imagePacket.createdAt),
                            imagePacket.pts,
                            imagePacket.width,
                            imagePacket.height,
                        )
                except Exception as ex:
                    self._decodeErrors += 1
                    warning("FrameRing packet decode failed", ex)
                finally:
                    decodeTimeNs: int = monotonic_ns() - decodeStartNs
                    self._decodeTimeNs += decodeTimeNs
                    self._maxDecodeTimeNs = max(self._maxDecodeTimeNs, decodeTimeNs)
            finally:
                self._queue.task_done()

    # ==================================================================================
    def _shrinkDecodeQueueLimit(self) -> None:
        if self._decodeQueueLimit <= self._config.decodeCapacity.minimum:
            return
        if self._queue.qsize() > self._decodeQueueLimit // 4:
            return

        self._decodeQueueLimit = max(
            self._config.decodeCapacity.minimum,
            self._decodeQueueLimit // 2,
        )
        self._config.decodeCapacity.current = self._decodeQueueLimit

    # ==================================================================================
    async def _publishFrame(
        self,
        frame: DECODEFORMAT,
        createdAt: int,
        pts: int,
        width: int,
        height: int,
    ) -> bool:
        filledCount: int = sum(slot.state is eSlotFlag.FILLED for slot in self._slots)
        highWatermark: int = max(1, ceil(self._size * C_RING_HIGH_WATERMARK))
        if filledCount >= highWatermark:
            self._evictOldest()

        idx: Optional[int] = self._pickWriteIndex()
        if idx is None:
            self._evictOldest()
            idx = self._pickWriteIndex()

        while idx is None:
            if self._stopping or not self._running:
                self._droppedFrames += 1
                return False

            self._slotChanged.clear()
            self._evictOldest()
            idx = self._pickWriteIndex()
            if idx is None:
                await self._slotChanged.wait()

        slot: RingSlot = self._slots[idx]
        try:
            slot.beginWrite(sequence=createdAt, pts=pts, width=width, height=height)
            self._slotChanged.set()
            slot.completeWrite(frame, width=width, height=height, pts=pts)
            self._publishedFrames += 1
            self._slotChanged.set()
            return True
        except Exception:
            slot.markFree()
            self._slotChanged.set()
            raise

    # ==================================================================================
    def _evictOldest(self) -> int:
        filledSlots: list[RingSlot] = [
            slot for slot in self._slots if slot.state is eSlotFlag.FILLED
        ]
        if len(filledSlots) <= 1:
            return 0

        newestCreatedAt: int = max(slot.createdAt for slot in filledSlots)
        eligibleSlots: list[RingSlot] = sorted(
            (
                slot for slot in filledSlots
                if slot.createdAt != newestCreatedAt and slot.readers == 0
            ),
            key=lambda slot: slot.createdAt,
        )
        if not eligibleSlots:
            return 0

        targetCount: int = max(1, ceil(len(filledSlots) * C_EVICT_PERCENT))
        evictedCount: int = min(targetCount, len(eligibleSlots))
        for slot in eligibleSlots[:evictedCount]:
            slot.markFree()

        self._evictedFrames += evictedCount
        if evictedCount:
            self._slotChanged.set()
        return evictedCount

    # ==================================================================================
    def latest(self) -> Optional[iRingSlot]:
        filledSlots: list[RingSlot] = [
            slot for slot in self._slots
            if slot.state is eSlotFlag.FILLED and slot.payload is not None
        ]
        if not filledSlots:
            return None

        best: RingSlot = max(filledSlots, key=lambda slot: slot.createdAt)
        best.acquire()
        return best

    # ==================================================================================
    async def next(self, currentSequence: Optional[int] = None) -> Optional[iRingSlot]:
        if currentSequence is None:
            async with self._defaultSequenceLock:
                slot: Optional[iRingSlot] = await self._findNext(self._currentSequence)
                if slot is not None:
                    self._currentSequence = slot.createdAt
                return slot

        return await self._findNext(int(currentSequence))

    # ==================================================================================
    async def _findNext(self, currentSequence: Optional[int]) -> Optional[iRingSlot]:
        while True:
            candidates: list[RingSlot] = [
                slot for slot in self._slots
                if slot.state in (eSlotFlag.WRITING, eSlotFlag.FILLED)
                and slot.createdAt > (currentSequence if currentSequence is not None else -1)
            ]
            if candidates:
                candidate: RingSlot = min(candidates, key=lambda slot: slot.createdAt)
                if candidate.state is eSlotFlag.WRITING:
                    self._slotChanged.clear()
                    await self._slotChanged.wait()
                    continue
                if candidate.payload is not None:
                    candidate.acquire()
                    return candidate

            if not self._running and (self._worker is None or self._worker.done()):
                return None

            self._slotChanged.clear()
            await self._slotChanged.wait()

    # ==================================================================================
    def release(self, slot: iRingSlot) -> None:
        if not isinstance(slot, RingSlot):
            raise TypeError("FrameRing.release expects a RingSlot acquired from this ring")
        if slot not in self._slots:
            raise ValueError("FrameRing.release received a slot owned by another ring")
        slot.release()
        self._slotChanged.set()

    # ==================================================================================
    def _pickWriteIndex(self) -> Optional[int]:
        for idx, slot in enumerate(self._slots):
            if slot.isWritable:
                return idx
        return None

    # ==================================================================================
    @staticmethod
    def _getVramUtilization() -> Optional[float]:
        try:
            from torch.cuda import is_available, mem_get_info
            if not is_available():
                return None
            freeBytes, totalBytes = mem_get_info()
            if totalBytes <= 0:
                return 1.0
            return (totalBytes - freeBytes) / totalBytes
        except Exception as ex:
            warning("Unable to query CUDA device memory utilization", ex)
            return 1.0

    # ==================================================================================
    @staticmethod
    def _releaseCachedVram() -> None:
        try:
            from torch.cuda import empty_cache, is_available
            if is_available():
                empty_cache()
        except Exception as ex:
            warning("Unable to release cached CUDA memory", ex)

    # ==================================================================================
    @property
    def size(self) -> int:
        return self._size

    @property
    def pending(self) -> int:
        return self._queue.qsize()

    @property
    def stats(self) -> dict[str, int | float | None]:
        return {
            "capacity": self._size,
            "filled": sum(slot.state is eSlotFlag.FILLED for slot in self._slots),
            "leased": sum(slot.readers > 0 for slot in self._slots),
            "pending": self._queue.qsize(),
            "decodeQueueLimit": self._decodeQueueLimit,
            "maxPending": self._maxPending,
            "decodedFrames": self._decodedFrames,
            "publishedFrames": self._publishedFrames,
            "evictedFrames": self._evictedFrames,
            "droppedFrames": self._droppedFrames,
            "invalidTimestampPackets": self._invalidTimestampPackets,
            "decodeErrors": self._decodeErrors,
            "decodeTimeNs": self._decodeTimeNs,
            "maxDecodeTimeNs": self._maxDecodeTimeNs,
            "vramUtilization": self._getVramUtilization(),
            "currentSequence": self._currentSequence,
        }


# ==================================================================================
__all__ = [
    "FrameRing",
    "C_DECODE_QUEUE_MINIMUM",
    "C_DECODE_QUEUE_MAXIMUM",
    "C_DECODE_QUEUE_SIZE",
    "C_EVICT_PERCENT",
    "C_RING_HIGH_WATERMARK",
]
# ==================================================================================
