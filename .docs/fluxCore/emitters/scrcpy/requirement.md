# Requirements — SCRCPYEmitter (Phase A)

## 1. Overview

Prepare `SCRCPYEmitter` for IPC bridging: typed event payloads without treating the emitter as the event argument type, plus structured `ON_ERROR`.

## 2. Functional requirements

- **FR-1:** `SCRCPYEmitter.toScrcpy(emitter)` is a **classmethod** that returns `SCRCPY` and does **not** construct a new `SCRCPY` instance.
- **FR-2:** `ON_METADATA_UPDATE` arguments are `SCRCPY` obtained via `toScrcpy`, not the emitter type as the documented payload.
- **FR-3:** `ON_FRAME` continues to pass `iFrame` (in-process only).
- **FR-4:** `ON_ERROR` passes `ScrcpyErrorFootprint` (`phase`, `message`, `serial`).
- **FR-5:** `ON_ERROR` is raised at: `initialize.deploy`, `initialize.socket`, `initialize.metadata`, `initialize.codec`, and unexpected `work` failures (not `CancelledError`, not skipped `InvalidDataError`).
- **FR-6:** After `ON_ERROR`, the original exception is still raised / propagates.

## 3. Non-goals (Phase A)

- IPC message types / bridge  
- Frame transport over IPC  
- Separate `ScrcpyFootprint` value type (use `SCRCPY` via `toScrcpy`)  
