# Requirements & Design Specifications

## 1. Project Overview
In-process frame ring that decodes image packets into cached slots without blocking the emitter receive loop, serving both latest-frame present and sequential capture consumers.

## 2. Functional Requirements
- **FR-1:** `publish` must not block on decode; schedule decode asynchronously.
- **FR-2:** Slot states: EMPTY | FREE | WRITING | FILLED. Ready-for-write = EMPTY | FREE.
- **FR-3:** Cache processed payload plus pts and created time from the packet contract (`pts`, `createdAt`, `width`, `height`).
- **FR-4:** `latest()` for present (may skip); `next()` + `release` for sequential recorder (must not skip).
- **FR-5:** Consumers must not tag slot state; only ring APIs change flags.
- **FR-6:** Grow when no writable slot; consecutive growth in a time window warns once then errors/refuses.

## 3. Non-Functional Requirements
- **NFR-1:** Prefer contract property access over `getattr` for packet fields.
- **NFR-2:** Payload getter must not mutate state.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Decode ownership on the ring
- **Affected Modules:** `fluxCore/stream/frameRing/__frameRing.py`
- **Divergence:** Ring invokes `packet.decode` instead of only storing foreign buffers.
- **Design Decision & Justification:** GPU path starts at decode; process-before-cache keeps one conversion point before FILLED.
- **Code Doc Cross-Reference:** `frameRing.md`, `slot/ringSlot.md`.
