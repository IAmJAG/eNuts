# ==================================================================================
from __future__ import annotations

from asyncio import Task

# ==================================================================================
from collections import deque
from time import monotonic_ns
from typing import Dict, List, Optional, Tuple

# ==================================================================================
from av import VideoCodecContext
from torch import Tensor

# ==================================================================================
from ...types import DECODEFORMAT
from ...types.interface.packets import iImagePacket
from ..__frameHeader import FrameHeader
from ..__streamHelpers import C_DEFAULT_RING_SIZE, validateRingSize
from .slot import RingSlot, eSlotFlag


# ==================================================================================
class FrameRing:
    def __init__(self, size: int = C_DEFAULT_RING_SIZE, canGrow: bool = True) -> None:
        self._size: int = validateRingSize(size)
        self._canGrow: bool = canGrow

        self._series: deque[float] = deque[float](maxlen=self._size)
        self._slots: Dict[float, RingSlot] = []
        for i in range(self._size): 
            self._slots.update(float(i), RingSlot())

    async def _decode(
        self, slot: RingSlot, packet: iImagePacket,
        decoder: VideoCodecContext, size: int = -1        
    ) -> DECODEFORMAT:
        try:
            slot.state = eSlotFlag.WRITING  # ensure that this coroutine set the target slot locked
            frame: DECODEFORMAT = packet.decode(decoder, size)
            slot.update(frame, packet.createdAt, packet.width, packet.height, packet.pts)            
            slot.state = eSlotFlag.FILLED            

        except Exception as e:
            raise e        

    def publish(self, packet: iImagePacket, decoder: VideoCodecContext, imageSize: int = -1) -> None:
        writeKey = self._pickWriteKey()
        slot: Optional[RingSlot] = self._slots.get(writeKey, None)                
        assert slot is not None, "Invalid writeKey"

        # locks the slot
        # prevents race condition on the order of the slots        
        slot.update(slot.payload, packet.createdAt, slot.width, slot.height, slot.pts)
        self._series.append(slot.sequence)
        createTask(self._decode, slot, packet, decoder, imageSize)

    def latest(self) -> Optional[DECODEFORMAT]:
        assert len(self._slots), "Ring is empty"

        bestKey: Optional[float] = None
        bestSlot: Optional[RingSlot] = self._slots.get(bestKey, None)

        for key in self._slots.keys():            
            slot: Optional[RingSlot] = self._slots.get(key, None)
            assert slot is not None, "Invalid key"

            if slot.state in [eSlotFlag.WRITING, eSlotFlag.FREE]: continue

            if bestSlot is None or slot.sequence > bestSlot.sequence:
                bestKey = key
                bestSlot = slot

        if bestKey is None or bestSlot is None:
            return None

        payload: Tensor = bestSlot.payload
        return payload.detach().clone()

    def next(self) -> Optional[DECODEFORMAT]:
        assert len(self._series), "Ring is empty"

        nextkey: Optional[RingSlot] = self._series[0]

        seriesLen: int = len(self._series)

        nextKey: Optional[float] = self._series.pop()
        while len(self._series) > 0:        
            nextKey = self._series.pop()
            slotKey: float = self._series[nextKey]            
            slot: Optional[RingSlot] = self._slots.get(slotKey, None)

            if slot is None: 
                warning(f"Invalid slotKey: {slotKey}")
                continue

            if slot.state in [eSlotFlag.WRITING, eSlotFlag.FREE]:
                if slot.state == eSlotFlag.WRITING:
                    self._series.append(slotKey)
                continue

        if nextkey is None: return None

        nextSlot: Optional[RingSlot] = self._slots.get(nextkey, None)
        if nextSlot is None: return None

        payload: Tensor = nextSlot.payload
        return payload.detach().clone()

    def _pickWriteKey(self) -> int:
        assert len(self._slots), "Ring is empty"

        slotKeys: List[float] = list(self._slots.keys())
        oldestKey: Optional[float] = min(slotKeys, default=slotKeys[0])

        slot: RingSlot
        for key in slotKeys:
            if slot.state in (eSlotFlag.WRITING, eSlotFlag.INUSE): continue

            slot = self._slots[key]
            if slot.state == eSlotFlag.FREE: return key

            if oldestKey is None or slot.sequence < oldestKey:
                oldestKey = slot.sequence

        return oldestKey

    @property
    def size(self) -> int:
        return self._size

# ==================================================================================
__all__ = ["FrameRing"]
# ==================================================================================