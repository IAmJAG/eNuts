## Overview & Design Context
`CaptureGLImage` subclasses `jAGQt.widgets.image.GLImage`. It displays stream frames like GLImage and additionally emits keyboard and mouse signals. It contains **no** recording state or inject logic.

* **Design Decision / Deviation Notes:** Mirrors `CaptureImage` (software Image path) so the KG Recorder OpenGL surface stays dumb; `application.recorder.KGRecorder` owns inject/log outside the Page.

---

## Classes

### `CaptureGLImage`
- **Purpose:** GL stream host that surfaces key/mouse events for external handlers.
- **Signals:** `keyPressed`, `keyReleased`, `mousePressed`, `mouseMoved`, `mouseReleased` (each carries the Qt event object).
- **Methods:** Overrides key/mouse handlers to emit then call `super()`. Enables `StrongFocus` and mouse tracking; mouse press requests focus for subsequent keys.

## Sample Usage

```python
from eNuts.UI.widgets import CaptureGLImage

view = CaptureGLImage(bg="#1a1a1a")
view.keyPressed.connect(handler)
view.mousePressed.connect(handler)
```
