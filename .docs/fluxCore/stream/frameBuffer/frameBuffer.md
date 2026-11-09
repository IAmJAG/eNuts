## Overview & Design Context
`FrameBuffer` provides a multi-consumer, zero-copy cache of decoded frames. Consumers access frames solely through `next(consumerId, sequence, timeout)`. Slots are `BufferSlot` instances that own their consumer set and a single timeout watcher.

* **Design Decision / Deviation Notes:** New type parallel to `FrameRing`. Only two states (locked/free). Eviction may invalidate locked slots. Configuration is `RingSlotConfiguration` nested under the fluxCore/stream path.

---

## Classes

### `FrameBuffer`
- **Purpose:** Owns the collection of `BufferSlot`s, applies growth and eviction policy, and exposes the single `next` entry point.
- **Methods:**
  - `publish(sequence, payload, pts, width, height)` -> Writes a decoded frame into a free or evicted slot.
  - `next(consumerId, sequence=None, timeout=None)` -> Acquires and returns the adjacent-greater or latest `BufferSlot`.

### `BufferSlot`
- **Purpose:** Holds one decoded snapshot, tracks bitwise consumer IDs, and owns the release timeout.
- **Methods:**
  - `acquire(consumerId, timeout)` -> Adds consumer and arms/resets timeout.
  - `release(consumerId=None)` -> Removes one or all consumers; frees payload when empty.
  - `write(...)` -> Stores a new snapshot (only when free or after eviction).

---

## Constants & Globals

### `RingSlotConfiguration`
- **Type:** Configuration section
- **Value / Description:** Supplies `bufferSizeMin`, `bufferSizeMax`, `vramCap`, `defaultReleaseTimeout`.

## Sample Usage

```python
from fluxCore.stream.frameBuffer import FrameBuffer

buffer = FrameBuffer(size=8)
buffer.publish(sequence=100, payload=tensor, pts=0, width=640, height=480)

slot = buffer.next(consumerId=0b0001)
if slot is not None:
    try:
        frame = slot.payload
    finally:
        slot.release(0b0001)
```
