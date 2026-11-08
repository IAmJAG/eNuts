# AI Handoff — eNuts stream / recorder pipeline

**Branch:** `development`  
**Updated:** 2026-11-08  
**Rule:** **Code is source of truth.** Docs adjust to code; do not change implementation to match design notes without an explicit code change request.

## FrameRing (revalidated after revert)

**Sources**
- `src/fluxCore/stream/frameRing/__frameRing.py`
- `src/fluxCore/stream/frameRing/slot/__ringSlot.py`
- `src/fluxCore/stream/frameRing/slot/__slotFlag.py`

**Behavior as coded**
- `publish`: contract fields `createdAt`/`pts`/`width`/`height`; `createTask(_decode)`; non-blocking.
- `_decode`: `await to_thread(packet.decode, ...)`; FILLED or abandon FREE.
- States: EMPTY | FREE | WRITING | FILLED.
- `latest()` / `next()` → `Optional[DECODEFORMAT]` (Tensor clone), **not** `(slot, payload)`.
- `release(slot: RingSlot)` requires the slot object; `next` does not return it.
- Grow: `_canGrow = maxGrow >= 0`; cap `C_GROW_MAX`; consecutive window warn then refuse.

**Open gaps visible in code (document only unless asked to change code)**
- `release` vs `next` return type mismatch for sequential consumers.
- `maxGrow` value not used as numeric cap (only enables/disables via `>= 0`).
- `LocalDeviceStream` may still use older decode path until wired to this `publish`.
- Smoke tests may still target old ring APIs.

## Docs
`.docs/fluxCore/stream/frameRing/` mirrors the above implementation.
