## Overview & Design Context

Historical **binary per-slot header** design notes for a GPU/IPC frame plane. Not the live in-process ring.

**Live code:** `src/fluxCore/stream/frameRing/` — see `.docs/fluxCore/stream/frameRing/`.

**Status:** Design archive for cross-process slot headers. In-process ring uses `RingSlot` + `eSlotFlag` (EMPTY/FREE/WRITING/FILLED), not this 40-byte wire layout.

---

## Constants (IPC design, not live ring)

| Name | Value / meaning |
|------|-----------------|
| `C_FRAME_SLOT_MAGIC` | `0x534C4F54` (`SLOT`) |
| `C_FRAME_SLOT_HEADER_SIZE` | 40 bytes |

### Wire layout (little-endian)

```text
magic u32 | seq u64 | pts u64 | w u32 | h u32 | stride u32 | format u32 | flags u32
```

## Related live code

- `src/fluxCore/stream/frameRing/__frameRing.py`
- `.docs/fluxCore/stream/frameRing/frameRing.md`
