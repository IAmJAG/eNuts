## Overview & Design Context
In-process frame ring under `fluxCore.stream.frameRing`. `publish` selects a slot, `beginWrite`s from packet contract fields, appends to `_order`, and schedules `_decode` via `createTask` (non-blocking). Decode uses `to_thread(packet.decode, ...)`. Present uses `latest()`; sequential path uses `next()` / `release(slot)`.

* **Design Decision / Deviation Notes:** Documentation follows the implementation. `latest`/`next` return cloned `DECODEFORMAT` (Tensor), not `(RingSlot, payload)`. `release` still takes a `RingSlot` — callers that only hold the payload from `next()` cannot release by identity unless they retain the slot another way. `maxGrow` ctor arg is stored only as `_canGrow = maxGrow >= 0`; grow cap is constant `C_GROW_MAX`.

---

## Classes

### `FrameRing`
- **Purpose:** Slot list + publish/decode + latest/next/release + optional grow.
- **Ctor:** `FrameRing(size=C_DEFAULT_RING_SIZE, maxGrow=C_GROW_MAX)`
- **Methods:**
  - `publish(packet, decoder, imageSize=-1)` — pick index, `beginWrite(sequence=packet.createdAt, pts, width, height)`, append `_order`, `createTask(_decode, ...)`.
  - `_decode(idx, slot, packet, decoder, imageSize)` — async; `to_thread(packet.decode)`; `completeWrite` or `_abandonWrite`.
  - `_abandonWrite(idx, slot)` — remove idx from `_order`, `markFree`.
  - `latest()` → `Optional[DECODEFORMAT]` — max `sequence` among FILLED; `payload.detach().clone()`.
  - `next()` → `Optional[DECODEFORMAT]` — head of `_order` if FILLED; `None` if WRITING; skips non-FILLED heads; returns clone only (does not pop or release).
  - `release(slot)` — if head of `_order` is that slot instance, pop and `markFree`.
  - `_pickWriteIndex()` — first `isWritable`, else oldest FILLED not in `_order`, else `None`.
  - `_tryGrow()` — if `_canGrow` and size < `C_GROW_MAX`; consecutive growth in `C_GROW_WINDOW_NS` warns then refuses.
- **Properties:** `size`

---

## Constants & Globals

### `C_GROW_STEP`
- **Type:** `int` — 4

### `C_GROW_MAX`
- **Type:** `int` — 256

### `C_GROW_WINDOW_NS`
- **Type:** `int` — 1_000_000_000

## Sample Usage

```python
from fluxCore.stream import FrameRing

ring = FrameRing(size=8)
ring.publish(packet, decoder)

image = ring.latest()   # Optional[DECODEFORMAT]
image = ring.next()     # Optional[DECODEFORMAT]; release(slot) needs RingSlot
```
