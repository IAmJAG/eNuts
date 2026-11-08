# FrameRing Requirements and Design

## Functional Requirements
- **FR-1:** `publish(packet, decoder)` is asynchronous and enqueues packets in a bounded queue.
- **FR-2:** Exactly one decoder worker invokes `packet.decode()` at a time, preserving submission order for a stateful codec context.
- **FR-3:** Queue saturation applies backpressure; it does not arbitrarily discard predictive video packets.
- **FR-4:** Decoded frames are published into reusable `RingSlot` instances.
- **FR-5:** `latest()` returns the newest FILLED `iRingSlot` and acquires a reader lease.
- **FR-6:** `release(slot)` relinquishes the lease. A leased slot is never selected for writing.
- **FR-7:** `next()` is retained as an alias for `latest()` and returns a leased slot.
- **FR-8:** `start()` starts the single worker; `stop()` drains queued work and awaits worker termination.
- **FR-9:** Growth remains guarded and bounded by `C_GROW_MAX`.

## Non-Functional Requirements
- No tensor clone is performed by the ring's read APIs.
- The event loop is not blocked by synchronous packet decoding; decode executes via `asyncio.to_thread`.
- Decoder calls are serialized to avoid concurrent access to one `VideoCodecContext`.
- Queue memory is bounded by `C_DECODE_QUEUE_SIZE` plus the fixed-size/growable decoded ring.

## Recording Separation
`KGRecorderService` records raw encoded `ON_FRAME` packet payloads directly from the emitter. It remains independent of `FrameRing`, so display frame reuse does not affect recording completeness.
