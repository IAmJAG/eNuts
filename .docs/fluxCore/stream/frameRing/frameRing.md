## Overview & Design Context
`FrameRing` owns process-then-cache for live frames. `publish` locks a slot (`WRITING`), schedules `packet.decode` off the caller via `createTask` + `to_thread`, then marks `FILLED`. Presenter uses `latest()`; recorder uses `next()` + `release(slot)`. Consumers never tag slots.

* **Design Decision / Deviation Notes:** Decode is async so the emitter `ON_FRAME` path does not block. Slot sequence is `packet.createdAt` (iPacket contract), not a new `monotonic_ns()` at publish. Growth uses consecutive-window warn then refuse.

---

## Classes

### `FrameRing`
- **Purpose:** Ordered slot buffer; decode+cache on publish path; dual read APIs.
- **Methods:**
  - `publish(packet, decoder, imageSize=-1)` — non-blocking; beginWrite + createTask(_decode).
  - `latest()` → `(RingSlot, payload) | None` — newest FILLED; does not free.
  - `next()` → `(RingSlot, payload) | None` — sequential head FILLED; `None` if head WRITING.
  - `release(slot)` — free sequential head only → FREE.
  - `_tryGrow()` — step 4, cap `maxGrow`, consecutive growth guard.

---

## Constants & Globals

### `C_GROW_STEP`
- **Type:** `int`
- **Value / Description:** 4 — slots added per grow.

### `C_GROW_MAX`
- **Type:** `int`
- **Value / Description:** 256 — default hard cap (`maxGrow` ctor arg).

### `C_GROW_WINDOW_NS`
- **Type:** `int`
- **Value / Description:** 1s window for consecutive-growth warn/error.

## Sample Usage

```python
from fluxCore.stream import FrameRing

ring = FrameRing(size=8, maxGrow=256)
ring.publish(packet, decoder)

item = ring.latest()
if item is not None:
    slot, image = item
    # present only

item = ring.next()
if item is not None:
    slot, image = item
    # record
    ring.release(slot)
```
