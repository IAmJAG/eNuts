# Implementation Details

## 1. Architecture Overview
`FrameBuffer` holds a list of `BufferSlot` objects. Decode calls `publish`. Consumers call `next`. Each `BufferSlot` maintains a set of consumer IDs and an asyncio Task for the release timeout. Growth and eviction are driven by `RingSlotConfiguration` limits and a simple VRAM probe.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/frameBuffer/__frameBuffer.py` | `.docs/fluxCore/stream/frameBuffer/frameBuffer.md` | Buffer collection, next, growth, eviction |
| `src/fluxCore/stream/frameBuffer/__bufferSlot.py` | `.docs/fluxCore/stream/frameBuffer/frameBuffer.md` | Slot lease, timeout, release |
| `src/fluxCore/stream/frameBuffer/__ringSlotConfiguration.py` | `.docs/fluxCore/stream/frameBuffer/frameBuffer.md` | Configurable limits and default timeout |
| `src/fluxCore/types/interface/stream/frameBuffer/` | `.docs/fluxCore/stream/frameBuffer/` | Protocols `iFrameBuffer`, `iBufferSlot` |

## 3. Core Workflows & Data Flow
1. Decoded frame arrives → `FrameBuffer.publish` finds a free slot or grows/evicts → `BufferSlot.write`.
2. Consumer calls `next(consumerId, sequence, timeout)` → slot located → `acquire` adds ID and arms timeout task → slot returned.
3. Consumer finishes → `slot.release(consumerId)` → if last consumer, payload cleared.
4. If consumer never releases, timeout task fires → `release()` clears all consumers.
5. Under pressure, `_evictOldest` calls `release()` on the oldest slot (locked or free) so the new frame can be written.
