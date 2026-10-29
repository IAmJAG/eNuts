# Implementation Details — SCRCPY emitter / bridge

## Architecture

```text
Main: ScrcpyProxyBridge  ⇄  Endpoint  ⇄  queues  ⇄  Endpoint  ⇄  ScrcpyRealBridge + emitter
```

## Module mapping

| Source | Docs |
|--------|------|
| `__SCRCPYEmitter.py` | `scrcpyEmitter.md` |
| `__footprint.py` | `footprint.md` |
| `__payloads.py` / `__messages.py` | `messages.md` |
| `__bridge.py` | `bridge.md` |

## Phase status

| Phase | Status |
|-------|--------|
| A–C | **Done** |
| D — inventory / doc close-out | **Done** |

## Notes

- Domain `send` leaves `ownerId` unset (peer default bridge).
- `Device` / `SCRCPY` expose `Properties` for Message encode/decode.
- Proxy correlation processor forwards to type handlers.
