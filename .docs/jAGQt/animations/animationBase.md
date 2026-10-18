## Overview & Design Context
Base class for custom, frame-driven animations in jAGQt. Subclasses implement `_onProgress(progress)` for values in `[0.0, 1.0]`. Built on `QVariantAnimation` for duration and easing.

* **Design Decision:** General animation base under `jAGQt.animations`, not icon-specific. Icon morph and other variants inherit this. Contract is `iAnimation` under `jAGQt.types.interface.animations`.

---

## Classes

### `AnimationBase`
- **Purpose:** Shared lifecycle (`start` / `stop` / `isRunning`) and progress driver for custom animations.
- **Methods:**
  - `start()` -> Starts (restarts if already running).
  - `stop()` -> Stops early; emits `stopped`.
  - `_onProgress(progress)` -> **Abstract**; apply one frame.
  - `_onStart()` / `_onStop()` / `_onFinished()` -> Optional hooks.
- **Properties:**
  - `isRunning` — whether the driver is running.
  - `durationMs` — duration in milliseconds.
  - `easing` — `QEasingCurve.Type`.
- **Signals:** `started`, `finished`, `stopped`.

---

## Sample Usage

```python
from jAGQt.animations import AnimationBase

class FadeProgress(AnimationBase):
    def _onProgress(self, progress: float) -> None:
        # apply progress
        ...

anim = FadeProgress(durationMs=300)
anim.finished.connect(lambda: None)
anim.start()
```
