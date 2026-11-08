# Implementation Details

## 1. Architecture Overview

```text
publish(packet, decoder)
  → pick EMPTY|FREE (or grow / overwrite FILLED not in order)
  → beginWrite(createdAt, pts, w, h)  # WRITING
  → append idx to _order
  → createTask(_decode)
       → to_thread(packet.decode)
       → completeWrite → FILLED  |  abandon → FREE

latest()  → max sequence among FILLED
next()    → head of _order if FILLED; None if WRITING
release() → pop head, markFree
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/frameRing/__frameRing.py` | `.docs/fluxCore/stream/frameRing/frameRing.md` | Ring + publish/decode/grow |
| `src/fluxCore/stream/frameRing/slot/__ringSlot.py` | `.docs/fluxCore/stream/frameRing/slot/ringSlot.md` | Slot cell |
| `src/fluxCore/stream/frameRing/slot/__slotFlag.py` | `.docs/fluxCore/stream/frameRing/slot/slotFlag.md` | EMPTY/FREE/WRITING/FILLED |
| `src/fluxCore/types/interface/packets/__imagePacket.py` | — | publish contract |

## 3. Core Workflows & Data Flow
1. Emitter delivers `iImagePacket` → `FrameRing.publish`.
2. Slot locked WRITING before task schedule so pick cannot reuse it.
3. `_order` records publish order at WRITING time so recorder order is preserved if decode finishes out of order.
4. Present reads `latest` only; recorder `next`/`release` drives FREE for rewrite.
