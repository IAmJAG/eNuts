# Requirements & Design Specifications

## 1. Project Overview
Presenter as implemented in `src/fluxCore/stream/__presenter.py`.

## 2. Functional Requirements (as coded)
- **FR-1:** Implement `iFrameConsumer`: `attachRing` / `detachRing` plus `iService` lifecycle via `AsyncService`.
- **FR-2:** View binding is Presenter-owned (`attachView` / `detachView`); not part of `iFrameConsumer`.
- **FR-3:** Work loop pulls `ring.latest()` only (may skip frames).
- **FR-4:** Call `view.present(frame)` with Tensor/handle; no convert/resize in Presenter.
- **FR-5:** Display rate via `AsyncService.throttle` (`displayFps` property).
- **FR-6:** Skip re-present when Tensor `data_ptr()` matches last successful present.
- **FR-7:** Tolerate missing ring/view and deleted Qt view (clear local refs).

## 3. Non-Functional Requirements
- **NFR-1:** Must not block the UI thread with convert/resize; those stay on the view path.
- **NFR-2:** Must not publish to or mutate the ring beyond pull APIs.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Skip without seq
- **Affected Modules:** `__presenter.py`
- **Divergence:** Ring `latest()` returns a cloned Tensor without seq metadata.
- **Design Decision & Justification:** Use optional `data_ptr` equality; throttle remains primary rate control.
- **Code Doc Cross-Reference:** `presenter.md`.
