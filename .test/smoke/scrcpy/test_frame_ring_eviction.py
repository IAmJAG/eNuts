# ==================================================================================
from __future__ import annotations

# ==================================================================================
import asyncio

# ==================================================================================
from fluxCore.stream.frameRing.__frameRing import FrameRing


# ==================================================================================
def _publish(ring: FrameRing, createdAt: int) -> None:
    asyncio.run(ring._publishFrame(object(), createdAt, createdAt, 1, 1))


def test_ring_evicts_oldest_twenty_percent_without_growing() -> None:
    ring = FrameRing(size=8)
    for createdAt in range(1, 9):
        _publish(ring, createdAt)
    _publish(ring, 9)
    assert ring.size == 8
    assert ring.stats["evictedFrames"] == 2
    assert ring.stats["droppedFrames"] == 0
    assert ring.stats["filled"] == 7
    latest = ring.latest()
    assert latest is not None
    try:
        assert latest.createdAt == 9
    finally:
        ring.release(latest)


def test_eviction_does_not_reuse_a_leased_slot() -> None:
    ring = FrameRing(size=2)
    _publish(ring, 1)
    _publish(ring, 2)
    leased = ring.latest()
    assert leased is not None and leased.createdAt == 2
    originalPayload = leased.payload
    _publish(ring, 3)
    assert leased.payload is originalPayload
    assert leased.createdAt == 2
    assert ring.size == 2
    latest = ring.latest()
    assert latest is not None
    try:
        assert latest.createdAt == 3
    finally:
        ring.release(latest)
        ring.release(leased)


def test_ring_waits_for_a_leased_slot_instead_of_dropping() -> None:
    ring = FrameRing(size=2)
    _publish(ring, 1)
    _publish(ring, 2)
    first = next(slot for slot in ring._slots if slot.createdAt == 1)
    second = next(slot for slot in ring._slots if slot.createdAt == 2)
    first.acquire()
    second.acquire()
    ring._running = True

    async def publishAfterRelease() -> None:
        task = asyncio.create_task(ring._publishFrame(object(), 3, 3, 1, 1))
        await asyncio.sleep(0)
        assert not task.done()
        first.release()
        ring._slotChanged.set()
        assert await task is True

    asyncio.run(publishAfterRelease())
    ring._running = False
    assert ring.stats["droppedFrames"] == 0
    second.release()


def test_explicit_consumer_cursors_advance_independently() -> None:
    ring = FrameRing(size=8)
    for createdAt in (10, 20, 30):
        _publish(ring, createdAt)

    async def readFrames() -> None:
        firstA = await ring.next(10)
        firstB = await ring.next(10)
        assert firstA is not None and firstA.createdAt == 20
        assert firstB is not None and firstB.createdAt == 20
        nextA = await ring.next(firstA.createdAt)
        assert nextA is not None and nextA.createdAt == 30
        assert ring._currentSequence is None
        for slot in (firstA, firstB, nextA):
            ring.release(slot)

    asyncio.run(readFrames())


def test_default_cursor_advances_only_for_default_next_calls() -> None:
    ring = FrameRing(size=8)
    for createdAt in (10, 20, 30):
        _publish(ring, createdAt)

    async def readFrames() -> None:
        first = await ring.next()
        assert first is not None and first.createdAt == 10
        assert ring._currentSequence == 10

        explicit = await ring.next(20)
        assert explicit is not None and explicit.createdAt == 30
        assert ring._currentSequence == 10

        second = await ring.next()
        assert second is not None and second.createdAt == 20
        assert ring._currentSequence == 20
        for slot in (first, explicit, second):
            ring.release(slot)

    asyncio.run(readFrames())


def test_consumer_cursor_skips_evicted_timestamps() -> None:
    ring = FrameRing(size=4)
    for createdAt in (10, 20, 30, 40, 50):
        _publish(ring, createdAt)

    async def readFrame() -> None:
        slot = await ring.next(10)
        assert slot is not None
        assert slot.createdAt > 10
        ring.release(slot)

    asyncio.run(readFrame())


def test_next_waits_for_a_future_publication() -> None:
    ring = FrameRing(size=4)
    ring._running = True

    async def readAfterPublish() -> None:
        task = asyncio.create_task(ring.next(10))
        await asyncio.sleep(0)
        assert not task.done()
        await ring._publishFrame(object(), 20, 20, 1, 1)
        slot = await task
        assert slot is not None and slot.createdAt == 20
        ring.release(slot)

    asyncio.run(readAfterPublish())
    ring._running = False


def test_concurrent_default_next_calls_advance_serially() -> None:
    ring = FrameRing(size=4)
    for createdAt in (10, 20, 30):
        _publish(ring, createdAt)

    async def readConcurrently() -> None:
        first, second = await asyncio.gather(ring.next(), ring.next())
        assert first is not None and second is not None
        assert (first.createdAt, second.createdAt) == (10, 20)
        assert ring._currentSequence == 20
        ring.release(first)
        ring.release(second)

    asyncio.run(readConcurrently())


class _TimestampPacket:
    def __init__(self, createdAt: int) -> None:
        self.createdAt = createdAt
        self.pts = createdAt
        self.width = 1
        self.height = 1

    def decode(self, decoder: object) -> object:
        return object()


def test_non_increasing_packet_timestamps_are_warned_and_skipped() -> None:
    ring = FrameRing(size=4)
    ring._getVramUtilization = lambda: None

    async def publishPackets() -> None:
        await ring.publish(_TimestampPacket(100), decoder=object())
        await ring.publish(_TimestampPacket(100))
        await ring.publish(_TimestampPacket(99))
        await ring.publish(_TimestampPacket(101))
        await ring._queue.join()
        await ring.stop()

    asyncio.run(publishPackets())
    assert ring.stats["invalidTimestampPackets"] == 2
    assert ring.stats["publishedFrames"] == 2
    assert ring.stats["droppedFrames"] == 0
