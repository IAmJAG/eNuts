# Implementation Details

## 1. Architecture Overview

```text
publish(packet, decoder, imageSize=-1)
  _pickWriteIndex() → EMPTY|FREE, else oldest FILLED not in _order
  beginWrite(createdAt, pts, w, h)  # WRITING
  _order.append(idx)
  createTask(_decode, idx, slot, packet, decoder, imageSize)
    to_thread(packet.decode, decoder, imageSize)
    completeWrite → FILLED  |  _abandonWrite → FREE + remove from _order

latest() → max sequence FILLED → payload.detach().clone()
next()   → while _order: head WRITING→None; non-FILLED→pop; FILLED→clone (no pop)
release(slot) → if head is slot: pop, markFree
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/frameRing/__frameRing.py` | `.docs/fluxCore/stream/frameRing/frameRing.md` | Ring |
| `src/fluxCore/stream/frameRing/slot/__ringSlot.py` | `.docs/fluxCore/stream/frameRing/slot/ringSlot.md` | Slot |
| `src/fluxCore/stream/frameRing/slot/__slotFlag.py` | `.docs/fluxCore/stream/frameRing/slot/slotFlag.md` | Flags |

## 3. Core Workflows & Data Flow
As in architecture diagram above. `_canGrow` is `maxGrow >= 0`; size limit for grow is always `C_GROW_MAX` in `_tryGrow`.
