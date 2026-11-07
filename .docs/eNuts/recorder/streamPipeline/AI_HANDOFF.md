# AI Handoff — eNuts stream / recorder pipeline

**Branch:** `development`  
**Updated:** 2026-11-07  
**Scope:** IAmJAG/eNuts only

## Locked product decisions

- **One emitter** only (no dual-emitter preview/capture).
- View and record share the **same** decoded frames (no resolution split).
- **UI / Presenter:** latest-only; may skip.
- **Recorder:** every frame, sequential; must not skip.
- **GPUReady codec alone is not ready:** live path still forces CPU via `toQImage` / `to_ndarray`. GPU path starts at decode; conversion stays with decode.
- Display widgets (`GLImage`) are **out of** ring design; Presenter may bind later.
- Decode remains on `fluxCore` packet `Frame.decode`; invocation is through ring-side processing (see below).

## Current mental model (2026-11-07)

```
SCRCPYEmitter
  ON_FRAME  ──────────────►  FrameRing.onFrame(Frame)
  other events (meta,        (decode+convert, cache slot)
  error, lifecycle) ──► LocalDeviceStream

LocalDeviceStream
  owns iFrameRing
  wires emitter → ring for ON_FRAME only
  owns non-frame emitter events and error policy
  does not present / does not record

FrameRing
  slot states: Empty | Free | Writing | Filled
  processes Frame before cache (ImageProcessor tight with Frame)
  caches: image payload, pts, created_ns (monotonic_ns)
  pts / timing from Frame; created_ns at accept
  growable when no Free/Empty for write; consecutive-growth guard
  usage recorded on slots; consumers do not tag slots

iImageConsumer (peers, not stacked)
  Presenter  → latest()
  Recorder   → sequential read (frees slots via ring APIs only)
```

## Slot states

| State | Meaning |
|-------|---------|
| **Empty** | Never written or cleared; available for write |
| **Free** | Released after sequential consumers advanced; available for write |
| **Writing** | Publish/decode in progress; not readable |
| **Filled** | Valid cached image + pts + created_ns; readable |

Ready-for-write = **Empty** or **Free**.  
No ready-for-write → grow (step + hard cap). Consecutive growth in window → warning, then error.

## Conversion ownership

- **Moved onto the ring path:** image is processed **before** the slot is marked **Filled**.
- ImageProcessor is **tightly coupled** with `Frame` (decode + convert; GPU starts at decode).
- Ring caches the **processed** image, not raw packets.
- Presenter/Recorder do not decode.

## LocalDeviceStream vs FrameRing

| Concern | Owner |
|---------|--------|
| `ON_FRAME` → process + publish | **FrameRing** (fed directly) |
| Metadata, lifecycle, **emitter errors** | **LocalDeviceStream** |
| Holding the ring instance | **LocalDeviceStream** |
| Present / record | **Peer consumers**, not the stream |

## Explicitly deferred / not ready

- Full GPU present (texture / no host RGB for UI).
- Cross-process IPC frame plane (docs exist; not the active fix path).
- Save/Open paired artefacts on KG Recorder page.

## Related code (today on development)

- `src/fluxCore/stream/__deviceStream.py` — current decode+ring+present combined
- `src/fluxCore/stream/__frameRing.py` — fixed slots, header+payload, no process
- `src/fluxCore/stream/__imageConverters.py` — CPU `toQImage` / `to_ndarray`
- `src/fluxCore/types/packets/__frame.py` — `Frame.decode(..., gpu=)`
- `src/fluxCore/emitters/__SCRCPYEmitter.py` — `MAX_SIZE`, `ON_FRAME`
- KG Recorder page owns session inject/log; controller in page not Shell

## Next implementation order (agreed direction)

1. Slot state machine + usage recording + grow + growth guard on ring contract
2. Ring accepts `Frame`, runs ImageProcessor, caches image/pts/created_ns
3. Wire emitter `ON_FRAME` → ring; stream keeps other events/errors
4. `iImageConsumer` Presenter + Recorder peers
5. GPU path inside ImageProcessor / `Frame.decode(gpu=True)` without mandatory `toQImage` for live UI

## Bitrate map (recommended, max_size → bps)

See conversation / session config: e.g. 720→6e6, 1080→10e6, 1920→16e6 (encode-side only).
