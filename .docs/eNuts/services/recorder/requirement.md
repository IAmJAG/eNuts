# Requirements & Design Specifications

## 1. Project Overview
Provide a shared recorder service for ENUTS K&G sessions: lossless-as-received encoded video plus synchronized input events, consumed by the KGRecorder page and future tooling.

## 2. Functional Requirements
- **FR-1:** Subscribe to emitter `ON_FRAME` and write every `payload` in arrival order to an elementary stream file (`video.h264`).
- **FR-2:** Do not use `FrameRing` / latest-wins display path for recording (no skip for UI load).
- **FR-3:** Log key and pointer events with relative timestamps into a single JSON array inside `session.json`.
- **FR-4:** `bind` → `start(sessionDir)` → `stop()` lifecycle; one active session per service instance.
- **FR-5:** `stop()` finalizes files and returns a result dict (paths, frameCount, events, durationSec).

## 3. Non-Functional Requirements
- **NFR-1:** Frame callback must not depend on decode or Qt presentation.
- **NFR-2:** No pause/resume recording API in v1.
- **NFR-3:** Use existing stack only (emitter frames + stdlib file/JSON; PyAV remains decode-side).

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Raw elementary stream instead of MP4 mux
- **Affected Modules:** `KGRecorderService`
- **Description of Standard / Best Practice:** Consumer apps often expect MP4/MKV containers.
- **Divergence:** v1 writes scrcpy/h264 payloads as received.
- **Design Decision & Justification:** Matches “use what is already available” and “as the packet arrived”; avoids new mux clock logic. Remux can be a later step.
- **Code Doc Cross-Reference:** `kgRecorderService.md` sample and constants.

### Issue / Item 2: Event-driven capture vs AsyncService work loop
- **Affected Modules:** `KGRecorderService.work`
- **Divergence:** `work` is a no-op; frames arrive via subscription.
- **Design Decision & Justification:** Emitter already delivers every packet on `ON_FRAME`; polling would risk skip or duplicate logic.
