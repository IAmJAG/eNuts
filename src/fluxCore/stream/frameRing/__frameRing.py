# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import to_thread
from time import monotonic_ns
from typing import List, Optional, Tuple

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from ...types import DECODEFORMAT
from ...types.interface.packets import iImagePacket
from ..__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize
from .slot import RingSlot, eSlotFlag

# ==================================================================================
# Growth policy
C_GROW_STEP: int = 4
C_GROW_MAX: int = 256
C_GROW_WINDOW_NS: int = 1_000_000_000  # 1s
# ==================================================================================


# ==================================================================================
class FrameRing:
    """Process-then-cache ring. Decode runs off the publish caller via createTask.

    Presenter: ``latest()`` — FILLED only; may skip.
    Recorder: ``next()`` + ``release(slot)`` — sequential; must not skip.
    Consumers do not tag slots; only ring APIs change state.
    """

    def __init__(
        self, size: int = C_DEFAULT_RING_SIZE, maxGrow: int = C_GROW_MAX
    ) -> None:
        self._size: int = validateRingSize(size)
        self._maxGrow: int = max(0, int(maxGrow))
        self._canGrow: bool = self._maxGrow > 0
        self._slots: List[RingSlot] = [RingSlot() for _ in range(self._size)]

        # Publish order (slot indices) for sequential next()
        self._order: List[int] = []

        # Growth guard
        self._lastGrowNs: int = 0
        self._consecutiveGrows: int = 0

    def publish(
        self,
        packet: iImagePacket,
        decoder: VideoCodecContext,
        imageSize: int = -1,
    ) -> None:
        idx = self._pickWriteIndex()
        if idx is None:
            if not self._tryGrow():
                raise RuntimeError("FrameRing: no writable slot and cannot grow")
            idx = self._pickWriteIndex()
            if idx is None:
                raise RuntimeError("FrameRing: grow succeeded but no writable slot")

        slot = self._slots[idx]

        # iImagePacket / iPacket contract properties only
        slot.beginWrite(
            sequence=packet.createdAt,
            pts=packet.pts,
            width=packet.width,
            height=packet.height,
        )
        self._order.append(idx)

        # Non-blocking: decode off emitter / ON_FRAME path
        createTask(self._decode, idx, slot, packet, decoder, imageSize)

    async def _decode(
        self,
        idx: int,
        slot: RingSlot,
        packet: iImagePacket,
        decoder: VideoCodecContext,
        imageSize: int = -1,
    ) -> None:
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
            warning(f"[FrameRing] _decode failed idx={idx}: {ex}")
            raise

    def _abandonWrite(self, idx: int, slot: RingSlot) -> None:
        """Decode failed or null frame: drop from order and free slot."""
        try:
            self._order = [i for i in self._order if i != idx]
        except Exception:
            pass
        finally:
            slot.markFree()

    def latest(self) -> Optional[Tuple[RingSlot, DECODEFORMAT]]:
        """Newest FILLED payload for present path. Does not free the slot."""
        best: Optional[RingSlot] = None
        for slot in self._slots:
            if slot.state is not eSlotFlag.FILLED or slot.payload is None:
                continue
            if best is None or slot.sequence > best.sequence:
                best = slot
        if best is None or best.payload is None:
            return None
        return best, best.payload

    def next(self) -> Optional[Tuple[RingSlot, DECODEFORMAT]]:
        """Head sequential FILLED frame. Caller must ``release(slot)`` when done."""
        while self._order:
            idx = self._order[0]
            slot = self._slots[idx]

            if slot.state is eSlotFlag.WRITING:
                return None

            if slot.state is not eSlotFlag.FILLED or slot.payload is None:
                self._order.pop(0)
                continue

            return slot, slot.payload

        return None

    def release(self, slot: RingSlot) -> None:
        """Recorder finished with sequential head → FREE (ready for write)."""
        if not self._order:
            return
        idx = self._order[0]
        if self._slots[idx] is not slot:
            return
        self._order.pop(0)
        slot.markFree()

    def _pickWriteIndex(self) -> Optional[int]:
        oldestIdx: Optional[int] = None
        oldestSeq: Optional[float] = None

        for i, slot in enumerate(self._slots):
            if slot.state is eSlotFlag.WRITING:
                continue
            if slot.isWritable:
                return i
            if i in self._order:
                continue
            if slot.state is eSlotFlag.FILLED:
                if oldestSeq is None or slot.sequence < oldestSeq:
                    oldestSeq = slot.sequence
                    oldestIdx = i

        return oldestIdx

    def _tryGrow(self) -> bool:
        if not self._canGrow or self._size >= self._maxGrow:
            return False

        now = monotonic_ns()
        if self._lastGrowNs and (now - self._lastGrowNs) < C_GROW_WINDOW_NS:
            self._consecutiveGrows += 1
            if self._consecutiveGrows == 1:
                warning("[FrameRing] consecutive growth (warning)")
            elif self._consecutiveGrows >= 2:
                error("[FrameRing] consecutive growth (error) — refusing grow")
                return False
        else:
            self._consecutiveGrows = 0

        step = min(C_GROW_STEP, self._maxGrow - self._size)
        if step <= 0:
            return False

        self._slots.extend(RingSlot() for _ in range(step))
        self._size += step
        self._lastGrowNs = now
        verbose(f"[FrameRing] grew by {step} → size={self._size}")
        return True

    @property
    def size(self) -> int:
        return self._size


# ==================================================================================
__all__ = ["FrameRing"]
# ==================================================================================
