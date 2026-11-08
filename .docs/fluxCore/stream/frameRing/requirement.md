# Requirements & Design Specifications

## 1. Project Overview
Frame ring as implemented in `src/fluxCore/stream/frameRing/__frameRing.py`.

## 2. Functional Requirements (as coded)
- **FR-1:** `publish` schedules decode with `createTask`; does not await decode on the caller.
- **FR-2:** Slots use `eSlotFlag`: EMPTY, FREE, WRITING, FILLED.
- **FR-3:** Write metadata from `packet.createdAt`, `packet.pts`, `packet.width`, `packet.height`.
- **FR-4:** `latest()` returns newest FILLED payload clone; `next()` returns sequential head payload clone when FILLED.
- **FR-5:** `release(slot)` frees only when `slot` is the current `_order` head instance.
- **FR-6:** Grow by `C_GROW_STEP` up to `C_GROW_MAX` when no writable index; consecutive grows in window warn then refuse.

## 3. Non-Functional Requirements
- **NFR-1:** Decode runs in `to_thread` so the event loop is not blocked by sync `packet.decode`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: `next` vs `release` API shape
- **Affected Modules:** `frameRing/__frameRing.py`
- **Divergence:** `next` does not return the `RingSlot`; `release` requires the slot object.
- **Design Decision & Justification:** Documented as implemented; any API change is a code change, not a doc-only fix.
- **Code Doc Cross-Reference:** `frameRing.md`.
