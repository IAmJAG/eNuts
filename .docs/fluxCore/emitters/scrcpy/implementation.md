# Implementation Details — SCRCPY emitter / bridge

## Architecture

```text
Main: ScrcpyProxyBridge  ⇄  Endpoint  ⇄  queues  ⇄  Endpoint  ⇄  ScrcpyRealBridge + emitter
```

In-process path used by eNuts DeviceManager:

```text
DeviceManager.ensureRunning
  → SCRCPYEmitter.initialize
      deployServer → video socket → control socket
      → _updateMetadata (timed header on video socket)
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
- Cause: `_updateMetadata` used unbounded `AsyncReadExact`. If the server never wrote the 76B header on the video channel, `ensureRunning` / `switchDevice` hung with no error.
- Fix: each header field is read via `_recvExact` + `asyncio.wait_for` (`C_METADATA_TIMEOUT_S = 5.0`). Timeout becomes `ConnectionError` and is raised through `initialize.metadata` so DeviceManager logs `ensureRunning initialize failed`.
- Progressive `trace("metadata begin …")` before the first read; existing success `metadata id=…` line retained.

## Phase status

| Phase | Status |
|-------|--------|
| A–C | **Done** |
| D — inventory / doc close-out | **Done** |
| Metadata read timeout | **Done** (2026-11-13) |

## Notes

- Domain `send` leaves `ownerId` unset (peer default bridge).
- `Device` / `SCRCPY` expose `Properties` for Message encode/decode.
- Proxy correlation processor forwards to type handlers.
- Diagnostic `trace` on deploy command and socket name remain until a clean run confirms header + frames.
