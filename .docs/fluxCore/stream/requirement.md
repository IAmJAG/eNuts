# Requirements & Design Specifications

## 1. Project Overview
In-process local device stream as implemented in `src/fluxCore/stream/__deviceStream.py`.

## 2. Functional Requirements (as coded)
- **FR-1:** `_onFrame` must only `ring.publish(packet, codec)` (no QImage decode, no present).
- **FR-2:** Register `iFrameConsumer` instances; start/stop them with the stream.
- **FR-3:** Default `Presenter` is registered at construction; view binding may go through `attachView`.
- **FR-4:** `switchDevice` coalesces concurrent requests to the latest serial.
- **FR-5:** Codec context is taken from the emitter (`ON_INITIALIZED` / `_codecContext`).

## 3. Non-Functional Requirements
- **NFR-1:** Publish path must not block the emitter on decode or UI paint.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Stream no longer presents
- **Affected Modules:** `__deviceStream.py`
- **Divergence:** Removed `StreamPresenter` + QImage path from the stream.
- **Design Decision & Justification:** Presenter is a peer consumer pulling from the ring.
- **Code Doc Cross-Reference:** `deviceStream.md`.
