# Implementation Details — SCRCPY emitter / bridge

## Architecture

```text
Main: ScrcpyProxyBridge  ⇄  Endpoint  ⇄  queues  ⇄  Endpoint  ⇄  ScrcpyRealBridge + emitter
```

In-process path used by eNuts DeviceManager:

```text
DeviceManager.ensureRunning
  → SCRCPYEmitter.initialize
      deployServer (log_level=info)
      → video socket
      → [tunnel_forward] read 1B dummy on video
      → control socket
      → _updateMetadata (64B name + codec + size, timed)
      → createCodecContext → ON_INITIALIZED
  → emitter.start → work → ON_FRAME
```

## Module mapping

| Source | Docs |
|--------|------|
| `__SCRCPYEmitter.py` | `scrcpyEmitter.md` |
| `__footprint.py` | `footprint.md` |
| `__payloads.py` / `__messages.py` | `messages.md` |
| `__bridge.py` | `bridge.md` |

## Metadata header (2026-11-13)

- Symptom: sockets connected (`scrcpy_00000001`) but no `metadata id=…` / `frame id=…` traces; UI still showed the kg-recorder page.
- Cause: `_updateMetadata` used unbounded `AsyncReadExact`. If the server never wrote the header on the video channel, `ensureRunning` / `switchDevice` hung with no error.
- Fix 1: each header field is read via `_recvExact` + `asyncio.wait_for` (`C_METADATA_TIMEOUT_S = 5.0`). Timeout → `ConnectionError` through `initialize.metadata`.
- Observation after Fix 1: timeout on first 64B read — server accepted both sockets but wrote **zero** bytes on video within 5s.
- Fix 2: match scrcpy `tunnel_forward` order. Server writes a 1-byte dummy on video **as soon as video is accepted**, before accepting control. Client now: video connect → read dummy → control connect → read name/codec/size. `log_level=info` so server stdout is drained during diagnosis.

## Phase status

| Phase | Status |
|-------|--------|
| A–C | **Done** |
| D — inventory / doc close-out | **Done** |
| Metadata read timeout | **Done** |
| tunnel_forward dummy-before-control | **Done** (2026-11-13) |

## Notes

- Domain `send` leaves `ownerId` unset (peer default bridge).
- `Device` / `SCRCPY` expose `Properties` for Message encode/decode.
- Proxy correlation processor forwards to type handlers.
- Diagnostic `trace` on deploy, socket name, dummy, and metadata remain until a clean run confirms header + frames.
