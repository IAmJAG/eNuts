# Requirements — SCRCPYEmitter (Phase A)

## 1. Overview

Prepare `SCRCPYEmitter` for IPC bridging: metadata uses a base `SCRCPY` snapshot; errors use `ScrcpyErrorFootprint`.

## 2. Functional requirements

- **FR-1:** `SCRCPYEmitter.toScrcpy(emitter)` is a **classmethod** that **constructs a base `SCRCPY`** (not `SCRCPYEmitter`, not any descendant), copies `id`/`name`/`codecId`/`width`/`height` from the emitter, and returns that instance. That `SCRCPY` is the metadata footprint — no parallel footprint class.
- **FR-2:** `ON_METADATA_UPDATE` passes the result of `toScrcpy`, never the emitter instance.
- **FR-3:** `ON_FRAME` continues to pass `iFrame` (in-process only).
- **FR-4:** `ON_ERROR` passes `ScrcpyErrorFootprint` (`phase`, `message`, `serial`).
- **FR-5:** `ON_ERROR` at: `initialize.deploy`, `initialize.socket`, `initialize.metadata`, `initialize.codec`, and unexpected `work` failures (not `CancelledError`, not skipped `InvalidDataError`).
- **FR-6:** After `ON_ERROR`, the original exception still propagates.

## 3. Non-goals (Phase A)

- IPC message types / bridge  
- Frame transport over IPC  
- A separate `ScrcpyFootprint` type (use base `SCRCPY` via `toScrcpy`)  
