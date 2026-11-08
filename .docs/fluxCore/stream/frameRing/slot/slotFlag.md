## Overview & Design Context
Slot lifecycle flags for `RingSlot` / `FrameRing`.

---

## Classes

### `eSlotFlag`
- **Purpose:** EMPTY | FREE | WRITING | FILLED.
- **Values:**
  - `EMPTY` — never used or cleared; writable.
  - `FREE` — released after sequential reader; writable.
  - `WRITING` — decode in progress; not readable, not reusable.
  - `FILLED` — valid payload; readable.

Ready-for-write = `EMPTY` | `FREE` (`RingSlot.isWritable`).
