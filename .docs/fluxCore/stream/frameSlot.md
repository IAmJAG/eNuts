## Overview & Design Context

Binary **per-slot header** design notes for the GPU/frame ring plane. Not a `Message` payload. Pixels are full reconstructed frames after decode; handles are opaque and platform-specific.

**Status:** Design / planned. No matching `src/fluxCore/**/frameSlot*` module on `development` today; active ring code is `src/fluxCore/stream/__frameRing.py`.

---

## Constants (design)

| Name | Value / meaning |
|------|-----------------|
| `C_FRAME_SLOT_MAGIC` | `0x534C4F54` (`SLOT`) |
| `C_FRAME_SLOT_HEADER_SIZE` | 40 bytes |
| `C_DEFAULT_RING_SIZE` | 3 |
| `C_MIN_RING_SIZE` / `C_MAX_RING_SIZE` | 2 / 4 |

### Wire layout (little-endian)

```text
magic u32 | seq u64 | pts u64 | w u32 | h u32 | stride u32 | format u32 | flags u32
```

---

## Types (design)

### `FramePresentFormat`

`UNKNOWN`, `RGBA8`, `BGRA8`, `RGB8`, `NV12`, `PLATFORM_OPAQUE`

### `FrameSlotFlags`

| Flag | Meaning |
|------|--------|
| `RESOLUTION_CHANGED` | Hint: geometry/format changed vs previous seq |
| `KEYFRAME` | Full refresh / discontinuity |
| `EOS` | End of stream |

### `FrameSlotHeader`

- `pack()` / `unpack()` / `validateMagic()`
- `pts` — presentation time µs (stream clock)
- Present skip: `shouldSkipPresent(seq, lastPresentedSeq)` — **not** content equality

### Ring helpers

- `pickWriteIndex(displayIndex=..., ringSize=...)` — never the display slot
- `nextRingIndex`, `clampRingSize`

## Related live code

- `src/fluxCore/stream/__frameRing.py`
- `src/fluxCore/stream/__deviceStream.py`
- `.docs/AI_HANDOFF.md` — project-level stream/recorder decisions
