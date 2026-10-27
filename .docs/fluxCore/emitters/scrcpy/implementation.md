# Implementation Details — SCRCPY emitter Phase A

## 1. Architecture

```text
SCRCPYEmitter (AsyncService + SCRCPY)
  toScrcpy(emitter) → base SCRCPY   # construct + copy attrs
  ON_METADATA_UPDATE(SCRCPY)
  ON_ERROR(phase, message, serial)
  ON_FRAME(iFrame)                  # local only
```

## 2. Module mapping

| Source | Docs |
|--------|------|
| `src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py` | `scrcpyEmitter.md` |

No `__footprint.py`.

## 3. Phase status

| Phase | Status |
|-------|--------|
| A — toScrcpy, events, ON_ERROR | **Done** |
| B — IPC messages | Pending |
| C — Bridge | Pending |
