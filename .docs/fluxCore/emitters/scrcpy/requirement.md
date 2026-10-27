# Requirements — SCRCPYEmitter (Phase A)

## 1. Overview

Metadata uses base `SCRCPY` via `toScrcpy`. Errors use `SCRCPYError` in module `__footprint.py`.

## 2. Functional requirements

- **FR-1:** `toScrcpy(emitter)` constructs a **base `SCRCPY`**, copies attributes, returns it (not the emitter).
- **FR-2:** `ON_METADATA_UPDATE` passes that `SCRCPY`.
- **FR-3:** `ON_FRAME` passes `iFrame` (in-process only).
- **FR-4:** `ON_ERROR` passes **`SCRCPYError`** (`phase`, `message`, `serial`). Module remains `__footprint.py`; class name is **`SCRCPYError`** (not `*Footprint`).
- **FR-5:** `ON_ERROR` at deploy / socket / metadata / codec / unexpected `work` failures.
- **FR-6:** After `ON_ERROR`, the exception still propagates.
