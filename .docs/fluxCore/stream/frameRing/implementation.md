# FrameRing Implementation

## Architecture

```text
LocalDeviceStream._onFrame(packet)
  await FrameRing.publish(packet, codec)
    elastic encoded-packet queue (minimum 4, maximum 256)
      one _decodeLoop task
        await to_thread(packet.decode, codec)
        await _publishFrame(decodedTensor, packet.createdAt)
          fixed-capacity RingSlot collection
          evict oldest eligible 20% under pressure
          completeWrite -> FILLED

Consumer A: await ring.next(lastCreatedAtA)
Consumer B: await ring.next(lastCreatedAtB)
  timestamp cursor lookup -> acquire lease -> return slot
  ring.release(slot)

Default consumer: await ring.next()
  lookup from _currentSequence -> acquire lease
  update _currentSequence -> return slot
```

## Ownership and sequence semantics

- `packet.createdAt` is the raw integer monotonic-nanosecond timestamp and is the frame sequence identity.
- Non-increasing timestamps are warned about and skipped before queue admission.
- `latest()` returns the newest FILLED slot and increments its reader count.
- `next(cursor)` returns the smallest available timestamp greater than `cursor`; an evicted cursor is advanced to the oldest available later frame.
- Explicit consumer cursors are independent and do not update `_currentSequence`.
- Default-cursor lookups are serialized and update `_currentSequence` only after successful lease acquisition.
- Multiple consumers can acquire leases on the same frame. A leased slot cannot be freed or reused.
- A WRITING candidate causes `next()` to wait for completion or invalidation. Stop wakes blocked readers.

## Capacity and backpressure

- Ring capacity is fixed by the constructor and is not derived from decode queue capacity.
- The decode queue starts at 4, grows on queue pressure up to 256 and shrinks as backlog drains, and remains hard-bounded at 256.
- VRAM utilization uses CUDA free/total device memory. Above 85%, the ring attempts eviction and CUDA cache release before rejecting an incoming packet.
- At 80% filled occupancy, evict the oldest eligible 20% (rounded up), excluding newest and leased slots.
- If no writable slot exists, retry the same eviction policy and wait for lease release. Do not arbitrarily discard decoded frames merely because all slots are leased.
- Stop rejects new submissions, wakes slot waiters, drains accepted packets, and then terminates the worker.

## Counters

`ring.stats` reports ring occupancy, active leases, pending packets, current decode queue limit, maximum queue depth, decoded/published/evicted/dropped counts, skipped timestamp count, decode errors and timing, VRAM utilization, and `_currentSequence`.
