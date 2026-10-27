# Requirements — SCRCPYEmitter (Phase A)

## 1. Overview

Prepare `SCRCPYEmitter` for IPC bridging: metadata uses a base `SCRCPY` snapshot; errors use plain event args.

## 2. Functional requirements

- **FR-1:** `SCRCPYEmitter.toScrcpy(emitter)` constructs a **base `SCRCPY`** (not the emitter), copies `id`/`name`/`codecId`/`width`/`height`, returns that instance.
- **FR-2:** `ON_METADATA_UPDATE` passes the result of `toScrcpy`, never the emitter instance.
- **FR-3:** `ON_FRAME` passes `iFrame` (in-process only).
- **FR-4:** `ON_ERROR` passes **`phase`, `message`, `serial`** as separate string arguments. No error footprint class.
- **FR-5:** `ON_ERROR` at: `initialize.deploy`, `initialize.socket`, `initialize.metadata`, `initialize.codec`, and unexpected `work` failures (not `CancelledError`, not skipped `InvalidDataError`).
- **FR-6:** After `ON_ERROR`, the original exception still propagates.

## 3. Non-goals

- Any footprint class  
- IPC messages / bridge (Phase B+)  
- Frame transport over IPC  
