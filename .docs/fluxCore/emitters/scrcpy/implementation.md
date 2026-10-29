# Implementation Details — SCRCPY emitter / bridge

## 1. Architecture Overview

```text
SCRCPYEmitter (AsyncService + SCRCPY)
  toScrcpy → base SCRCPY
  asyncRaiseEvent(ON_*)

Messages (Phase B)
  ScrcpyInitializeMessage(ScrcpyInitParams)
  ScrcpyStartMessage / ScrcpyStopMessage
  ScrcpyMetadataMessage(SCRCPY)
  ScrcpyErrorMessage(SCRCPYError)

[Phase C] Bridge real | proxy ⇄ Endpoint
```

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py` | `scrcpyEmitter.md` | Emitter lifecycle, events, `toScrcpy` |
| `src/fluxCore/emitters/scrcpy/__footprint.py` | `footprint.md` | `SCRCPYError` |
| `src/fluxCore/emitters/scrcpy/__payloads.py` | `messages.md` | `ScrcpyInitParams` |
| `src/fluxCore/emitters/scrcpy/__messages.py` | `messages.md` | IPC message subclasses |
| `src/fluxCore/emitters/scrcpy/__bridge.py` | `bridge.md` | Real/proxy bridge — **pending** |

## 3. Phase status

| Phase | Status |
|-------|--------|
| A | **Done** |
| B | **Done** |
| C | Pending |
