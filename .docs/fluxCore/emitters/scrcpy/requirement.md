# Requirements & Design Specifications — SCRCPY emitter / bridge

## 1. Project Overview

Prepare `SCRCPYEmitter` so it can be driven across process boundaries using `jAGFx.IPC`. Phase A hardens local events. Phases B–C add messages and bridges. Frames stay in-process until a later shared-memory path.

## 2. Functional Requirements

### Phase A (done)

- **FR-A1:** `SCRCPYEmitter.toScrcpy(emitter)` constructs a **base `SCRCPY`** (not the emitter), copies `id`/`name`/`codecId`/`width`/`height`, returns that instance.
- **FR-A2:** `ON_METADATA_UPDATE` receives that base `SCRCPY` only.
- **FR-A3:** `ON_FRAME` receives `iFrame` (in-process only).
- **FR-A4:** `ON_ERROR` receives **`SCRCPYError`** (`phase`, `message`, `serial`) from `__footprint.py`. Class name is `SCRCPYError`, not `*Footprint`.
- **FR-A5:** `ON_ERROR` at `initialize.deploy`, `initialize.socket`, `initialize.metadata`, `initialize.codec`, and unexpected `work` failures (not `CancelledError`, not skipped `InvalidDataError`). Exception still propagates after the event.
- **FR-A6:** All events raised by `SCRCPYEmitter` use **`asyncRaiseEvent`** (awaited).

### Phase B (planned)

- **FR-B1:** Define `ScrcpyInitParams` and five IPC `Message` subclasses under `emitters/scrcpy/` (not under `jAGFx.IPC`).
- **FR-B2:** Initialize is correlated; completion uses terminal metadata or terminal error. Start/Stop are fire-and-forget unless later extended.

### Phase C (planned)

- **FR-C1:** Real bridge owns `SCRCPYEmitter`; proxy bridge exposes command/event surface on the peer.
- **FR-C2:** Both register type-keyed handlers on the local `Endpoint`.

## 3. Non-Functional Requirements

- **NFR-1:** Domain messages must not import into `jAGFx.IPC` core.
- **NFR-2:** No live emitter, socket, or codec object on the IPC queue.
- **NFR-3:** Docs under `.docs/fluxCore/emitters/scrcpy/` stay in sync with code in the same change set.

## 4. Design Decisions

### Metadata snapshot is base `SCRCPY`

- **Affected:** `__SCRCPYEmitter.py`
- **Decision:** Reuse `SCRCPY` via `toScrcpy` (construct + copy attributes).
- **Justification:** Avoid a second type that duplicates device fields.

### Error payload is `SCRCPYError` in `__footprint.py`

- **Affected:** `__footprint.py`, emitter `ON_ERROR`
- **Decision:** Module name `__footprint.py`; class is `SCRCPYError`.
- **Justification:** Errors are not a `SCRCPY`; still need a small serializable payload for events and future IPC.
