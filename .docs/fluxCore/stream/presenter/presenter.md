## Overview & Design Context
Display-side `iFrameConsumer` under `fluxCore.stream`. Pulls `ring.latest()`, applies Presenter-owned skip/timing policy, and calls `iFrameView.present(frame)`. Convert, resize, and paint belong to the view. View attach/detach are Presenter-owned and are not on `iFrameConsumer`.

* **Design Decision / Deviation Notes:** Replaces the transitional `StreamPresenter` (QObject + `presentExternal`) for the new ring path. Does not decode or resize. Does not hold stream or emitter references.

---

## Classes

### `Presenter`
- **Bases:** `AsyncService` (satisfies `iFrameConsumer` / `iService`)
- **Ctor:** `Presenter(displayFps=C_DEFAULT_DISPLAY_FPS, name=None)` — throttle set to `1.0 / displayFps`
- **Methods:**
  - `attachRing(ring)` / `detachRing()` — `iFrameConsumer` source binding
  - `attachView(view)` / `detachView()` — Presenter-owned; `detachView` calls `view.clear()` when present
  - `_present()` — async work: guard ring/view, `latest()`, optional `data_ptr` skip, `view.present(frame)`
- **Properties:** `displayFps` (get/set maps to `throttle`)

---

## Constants & Globals

### `C_DEFAULT_DISPLAY_FPS`
- **Type:** `float` — 30.0

## Sample Usage

```python
from fluxCore.stream import Presenter, FrameRing

presenter = Presenter(displayFps=30.0)
presenter.attachRing(ring)
presenter.attachView(captureGLImage)
presenter.start()
```
