## Overview & Design Context

Binary **per-slot header** for the GPU frame plane. Not a `Message` payload. Pixels are full reconstructed frames after decode; handles are opaque and platform-specific.

Source: `src/fluxCore/emitters/scrcpy/__frameSlot.py`

---

## Constants

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

## Types

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
- `pts` — presentation time µs (stream clock); used later for FPS pacing
- Present skip: `shouldSkipPresent(seq, lastPresentedSeq)` — **not** content equality

### Ring helpers

- `pickWriteIndex(displayIndex=..., ringSize=...)` — never the display slot
- `nextRingIndex`, `clampRingSize`

---

## Sample Usage

```python
from fluxCore.emitters.scrcpy import (
    makeFrameSlotHeader, FrameSlotHeader, FramePresentFormat, FrameSlotFlags,
    pickWriteIndex, shouldSkipPresent,
)

h = makeFrameSlotHeader(
    seq=1, pts=0, width=1080, height=1920,
    format=FramePresentFormat.RGBA8,
    flags=FrameSlotFlags.KEYFRAME,
)
raw = h.pack()
back = FrameSlotHeader.unpack(raw)
writeIdx = pickWriteIndex(displayIndex=0, ringSize=3)
```
