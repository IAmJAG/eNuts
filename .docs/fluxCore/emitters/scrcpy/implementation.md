# Implementation Details — SCRCPY emitter / bridge

## 1. Architecture Overview

```text
SCRCPYEmitter (AsyncService + SCRCPY)
  toScrcpy(emitter) → base SCRCPY
  asyncRaiseEvent(ON_METADATA_UPDATE, SCRCPY)
  asyncRaiseEvent(ON_FRAME, iFrame)          # local only
  asyncRaiseEvent(ON_ERROR, SCRCPYError)
  asyncRaiseEvent(ON_INITIALIZED, codec)     # local only

[Phase B] Message types + ScrcpyInitParams
[Phase C] Bridge real | proxy ⇄ Endpoint ⇄ peer process
```

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py` | `scrcpyEmitter.md` | Emitter lifecycle, events, `toScrcpy` |
| `src/fluxCore/emitters/scrcpy/__footprint.py` | `footprint.md` | `SCRCPYError` |
| `src/fluxCore/emitters/scrcpy/__payloads.py` | `messages.md` (B) | `ScrcpyInitParams` — **pending** |
| `src/fluxCore/emitters/scrcpy/__messages.py` | `messages.md` (B) | IPC message subclasses — **pending** |
| `src/fluxCore/emitters/scrcpy/__bridge.py` | `bridge.md` (C) | Real/proxy bridge — **pending** |

## 3. Core Workflows

### Initialize (local)

1. `setSuppressEvent(True)` during setup as implemented.
2. Deploy server → sockets → `_updateMetadata` → codec.
3. On failure: `await _raiseError(phase, message)` then re-raise.
4. On success: `await asyncRaiseEvent("ON_INITIALIZED", codecContext)`.

### Metadata event

1. Parse stream header; `update` geometry on emitter.
2. `me = toScrcpy(self)` → base `SCRCPY`.
3. `await asyncRaiseEvent("ON_METADATA_UPDATE", me)`.

### Work loop

1. Receive frame → `await asyncRaiseEvent("ON_FRAME", frame)`.
2. `InvalidDataError` → yield and continue.
3. Other errors → `await _raiseError("work", ...)` then raise.

### Cross-process (planned B/C)

Main sends `ScrcpyInitializeMessage` → client bridge runs `initialize` → replies with metadata and/or error on the same correlation when required.

## 4. Phase status

| Phase | Status |
|-------|--------|
| A | **Done** |
| B | Pending |
| C | Pending |
