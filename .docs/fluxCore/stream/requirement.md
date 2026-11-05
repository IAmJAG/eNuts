# Requirements & Design Specifications

## 1. Project Overview
In-process device stream abstraction for live view (and later recording) without the page owning emitter lifecycle.

## 2. Functional Requirements
- **FR-1:** One stream instance can switch serials without recreating decoder/ring/presenter.
- **FR-2:** `switchDevice` must serialize concurrent combo changes.
- **FR-3:** Decode happens once inside the stream; consumers receive `FrameHeader` + `QImage`.
- **FR-4:** Latest-frame presentation via `FrameRing` + `StreamPresenter` (or `view.image` fallback).
- **FR-5:** Start path must use `DeviceManager.ensureRunning` so initialize is awaited.

## 3. Non-Functional Requirements
- **NFR-1:** Incomplete emitter socket teardown remains an emitter concern; stream only calls `stop()`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Page must not own emitter
- **Affected Modules:** `eNuts/UI/pages/__kgRecorder.py`, `fluxCore/stream/__deviceStream.py`
- **Divergence:** Page routes device changes only through `LocalDeviceStream.switchDevice`.
- **Design Decision & Justification:** Removes stop/start/subscribe races and double-decode on the UI path.
