## Overview & Design Context
One cell in `FrameRing`. Holds processed payload, pts, dimensions, and sequence (`packet.createdAt`). State transitions only through explicit methods.

* **Design Decision / Deviation Notes:** `payload` is read-only and does not set INUSE; usage is owned by the ring via `release`.

---

## Classes

### `RingSlot`
- **Purpose:** Storage + lifecycle for one cached frame.
- **Methods:**
  - `beginWrite(sequence, pts, width, height)` → WRITING, clear payload.
  - `completeWrite(payload, width, height, pts=None)` → FILLED.
  - `markFree()` → FREE, drop payload.
  - `clear()` → EMPTY.
- **Properties:** `state`, `sequence`, `pts`, `width`, `height`, `payload`, `isWritable`.

## Sample Usage

```python
# Prefer FrameRing APIs; slot methods are used by the ring internally.
slot.beginWrite(packet.createdAt, packet.pts, packet.width, packet.height)
slot.completeWrite(frame, packet.width, packet.height, packet.pts)
```
