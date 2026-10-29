# Requirements & Design Specifications — SCRCPY emitter / bridge

## 1. Project Overview

Prepare `SCRCPYEmitter` for cross-process control via `jAGFx.IPC`. Phase A hardens local events. Phase B defines wire messages. Phase C implements bridges.

## 2. Functional Requirements

### Phase A (done)

- **FR-A1–A6:** `toScrcpy`, event payloads, `SCRCPYError`, `asyncRaiseEvent` (see prior plan).

### Phase B (done)

- **FR-B1:** `ScrcpyInitParams` and five IPC `Message` subclasses under `emitters/scrcpy/` (not under `jAGFx.IPC`).
- **FR-B2:** Initialize is correlated; completion uses terminal metadata or terminal error. Start/Stop are fire-and-forget.

### Phase C (planned)

- **FR-C1:** Real bridge owns `SCRCPYEmitter`; proxy on the peer.
- **FR-C2:** Both register type-keyed handlers on the local `Endpoint`.

## 3. Non-Functional Requirements

- **NFR-1:** Domain messages must not import into `jAGFx.IPC` core.
- **NFR-2:** No live emitter, socket, or codec object on the IPC queue.
- **NFR-3:** Docs stay in sync with code in the same change set.
