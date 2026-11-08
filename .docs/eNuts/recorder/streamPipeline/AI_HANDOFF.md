# AI Handoff — eNuts stream / recorder pipeline

**Branch:** `development`  
**Updated:** 2026-11-08  
**Scope:** IAmJAG/eNuts only

## Locked product decisions

- **One emitter** only (no dual-emitter).
- View and record share the **same** decoded frames.
- **UI / Presenter:** `latest()`; may skip.
- **Recorder:** `next()` + `release(slot)`; must not skip.
- Decode on ring publish path via `createTask` + `to_thread` (non-blocking for emitter).
- Packet fields: **contract properties only** (`createdAt`, `pts`, `width`, `height`).
- Display widgets out of ring design.

## Live FrameRing (validated 2026-11-08)

**Paths**

- `src/fluxCore/stream/frameRing/__frameRing.py`
- `src/fluxCore/stream/frameRing/slot/__ringSlot.py`
- `src/fluxCore/stream/frameRing/slot/__slotFlag.py`

**Slot states:** EMPTY | FREE | WRITING | FILLED  
**Ready-for-write:** EMPTY | FREE  
**Growth:** step 4, `maxGrow` (default 256), consecutive window warn → refuse  
**Sequence:** `packet.createdAt`  
**latest/next:** return `(RingSlot, payload)`; recorder must `release(slot)`

## Still pending

- Wire `LocalDeviceStream` so `ON_FRAME` calls `FrameRing.publish(packet, decoder)` (stream keeps non-frame events/errors).
- Parent stream docs still mention older QImage decode-in-stream path — partial drift flagged in `implementation.md`.
- Smoke tests under `.test/smoke/scrcpy/test_frame_ring.py` still target old emitters.scrcpy API — need rewrite.
- Full GPU present path (no host RGB for UI) not done.
- `iPacket.createdAt` generic property implementation may need care when comparing sequences.

## Docs

- `.docs/fluxCore/stream/frameRing/` (+ `slot/`)
- `.docs/fluxCore/stream/implementation.md` (updated mapping)
- `.docs/fluxCore/stream/frameSlot.md` (IPC design archive only)
