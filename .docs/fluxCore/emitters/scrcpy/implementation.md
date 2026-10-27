# Implementation Details — SCRCPY emitter Phase A

## 1. Architecture

```text
SCRCPYEmitter (AsyncService + SCRCPY)
  toScrcpy(emitter) → SCRCPY   # same object
  ON_METADATA_UPDATE(SCRCPY)
  ON_ERROR(ScrcpyErrorFootprint)
  ON_FRAME(iFrame)             # local only
```

## 2. Module mapping

| Source | Docs |
|--------|------|
| `src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py` | `scrcpyEmitter.md` |
| `src/fluxCore/emitters/scrcpy/__footprint.py` | `footprint.md` |

## 3. Phase status

| Phase | Status |
|-------|--------|
| A — events / toScrcpy / ON_ERROR | **Done** |
| B — IPC messages | Pending |
| C — Bridge | Pending |
