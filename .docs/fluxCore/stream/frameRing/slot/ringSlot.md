## Overview & Design Context
`RingSlot` cell used by `FrameRing`. Implementation: `src/fluxCore/stream/frameRing/slot/__ringSlot.py`.

---

## Classes

### `RingSlot`
- **Purpose:** Holds state, sequence, pts, width, height, payload.
- **Methods:**
  - `beginWrite(sequence, pts, width=0, height=0)` → WRITING, clear payload.
  - `completeWrite(payload, width, height, pts=None)` → FILLED.
  - `markFree()` → FREE, payload None.
  - `clear()` → EMPTY, zeros fields.
- **Properties:** `state`, `sequence` (int), `pts`, `width`, `height`, `payload` (read-only, no state change), `isWritable` (EMPTY or FREE).

## Sample Usage

Used by `FrameRing` internally on publish/decode/release paths.
