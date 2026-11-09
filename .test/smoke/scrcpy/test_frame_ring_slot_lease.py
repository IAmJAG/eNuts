from __future__ import annotations

import pytest

from fluxCore.stream.frameRing.slot import RingSlot
from fluxCore.types import eSlotFlag


def test_ring_slot_cannot_be_reused_while_leased() -> None:
    slot = RingSlot()
    payload = object()
    slot.beginWrite(sequence=1, pts=10, width=20, height=30)
    slot.completeWrite(payload, width=20, height=30, pts=10)

    slot.acquire()
    assert slot.readers == 1
    assert slot.payload is payload
    assert not slot.isWritable

    with pytest.raises(RuntimeError):
        slot.beginWrite(sequence=2, pts=20)
    with pytest.raises(RuntimeError):
        slot.markFree()

    slot.release()
    assert slot.readers == 0
    assert not slot.isWritable


def test_ring_slot_becomes_writable_after_free() -> None:
    slot = RingSlot()
    slot.beginWrite(sequence=1, pts=10)
    slot.completeWrite(object(), width=1, height=1)
    slot.markFree()

    assert slot.state is eSlotFlag.FREE
    assert slot.payload is None
    assert slot.createdAt == 0
    assert slot.isWritable
