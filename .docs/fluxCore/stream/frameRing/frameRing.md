# FrameRing

`FrameRing` serializes packet decoding through one elastic, bounded asynchronous queue and stores decoded tensors in reusable `RingSlot` objects. Ring capacity is fixed at construction and is independent of decode queue capacity.

## API

- `start() -> None`: start the single decode worker.
- `publish(packet, decoder=None) -> Awaitable[None]`: validate the packet's monotonic timestamp and enqueue it. A decoder may be supplied or configured with `setDecoder()`.
- `latest() -> Optional[iRingSlot]`: acquire and return the newest filled slot.
- `next(currentSequence=None) -> Awaitable[Optional[iRingSlot]]`: return the smallest available `createdAt` strictly greater than the supplied cursor. When omitted or `None`, the ring uses `_currentSequence` and advances it only after acquiring a slot.
- `release(slot) -> None`: release exactly one lease acquired through `latest()` or `next()`.
- `stop() -> Awaitable[None]`: stop accepting new packets, drain queued packets, and await worker termination.
- `size`: fixed number of ring slots.
- `pending`: number of encoded packets awaiting decode.

## Sequence and consumer contract

`packet.createdAt` is the sequence identity. It is the raw integer returned by `time.monotonic_ns()` and is comparable only within the same monotonic clock domain. A packet whose timestamp is less than or equal to the last accepted timestamp is warned about and skipped; it does not advance the accepted timestamp.

Consumers may keep independent cursors:

```python
slot = await ring.next(currentSequence)
if slot is not None:
    try:
        frame = slot.payload
        if frame is not None:
            view.present(frame)
        currentSequence = slot.createdAt
    finally:
        ring.release(slot)
```

Calling `await ring.next()` uses the ring-managed `_currentSequence`. Calling `await ring.next(timestamp)` uses only the supplied consumer cursor and never changes `_currentSequence`. Concurrent default-cursor calls are serialized. Multiple consumers may lease the same filled slot independently.

The lookup skips timestamps that have already been evicted and returns the oldest currently available timestamp greater than the cursor. It waits when the earliest matching slot is WRITING or when no later frame has arrived. Stop wakes waiting consumers; once no later frame is available, `next()` returns `None`.

Always release a returned slot exactly once. The payload is the original decoded tensor; do not use it after releasing the slot unless the consumer has made its own copy.

## Capacity, eviction and VRAM admission

- Ring capacity is fixed at the validated constructor size and is never resized by decode queue settings.
- Decode queue capacity starts at 4, grows on pressure up to 256 and shrinks as backlog drains, and uses a hard queue bound of 256.
- CUDA utilization is measured with `torch.cuda.mem_get_info()` as `(total - free) / total`. On systems without CUDA, VRAM-based admission is not applied.
- Above the configured 85% VRAM cap, the ring attempts its normal eviction policy and releases cached CUDA allocations. If utilization remains above the cap, the incoming packet is counted as dropped.
- At or above 80% FILLED occupancy, the ring evicts the oldest eligible 20% of FILLED slots, rounded up. The newest slot and leased slots are protected.
- If no writable slot exists, the same eviction policy is attempted as a fallback. If all candidates remain leased, the decode worker waits for a lease release instead of arbitrarily dropping the decoded frame.

## Measurements

`ring.stats` includes capacity, occupancy, leases, pending packets, current decode queue limit, queue high-water mark, decoded/published/evicted/dropped counts, non-increasing timestamp count, decode errors, decode durations, VRAM utilization, and the default sequence cursor.
