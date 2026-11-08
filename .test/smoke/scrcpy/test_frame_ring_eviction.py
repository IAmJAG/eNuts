from __future__ import annotations

from pathlib import Path
import sys

_REPO_SRC = Path(__file__).resolve().parents[3] / "src"
if str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))

from fluxCore.stream.frameRing.__frameRing import FrameRing


def _publish(ring: FrameRing, sequence: int) -> None:
    ring._publishFrame(object(), sequence, sequence, 1, 1)


def test_ring_evicts_oldest_twenty_percent_without_growing() -> None:
    ring = FrameRing(size=8)
    for sequence in range(1, 9):
        _publish(ring, sequence)
    _publish(ring, 9)
    assert ring.size == 8
    assert ring.stats["evictedFrames"] == 2
    assert ring.stats["droppedFrames"] == 0
    assert ring.stats["filled"] == 7
    latest = ring.latest()
    assert latest is not None
    try:
        assert latest.sequence == 9
    finally:
        ring.release(latest)


def test_eviction_does_not_reuse_a_leased_slot() -> None:
    ring = FrameRing(size=2)
    _publish(ring, 1)
    _publish(ring, 2)
    leased = ring.latest()
    assert leased is not None and leased.sequence == 2
    originalPayload = leased.payload
    _publish(ring, 3)
    assert leased.payload is originalPayload
    assert leased.sequence == 2
    assert ring.size == 2
    latest = ring.latest()
    assert latest is not None
    try:
        assert latest.sequence == 3
    finally:
        ring.release(latest)
        ring.release(leased)


def test_ring_drops_decoded_frame_when_every_slot_is_leased() -> None:
    ring = FrameRing(size=2)
    _publish(ring, 1)
    _publish(ring, 2)
    first = next(slot for slot in ring._slots if slot.sequence == 1)
    second = next(slot for slot in ring._slots if slot.sequence == 2)
    first.acquire()
    second.acquire()
    _publish(ring, 3)
    assert ring.size == 2
    assert ring.stats["droppedFrames"] == 1
    assert ring.stats["evictedFrames"] == 0
    first.release()
    second.release()
