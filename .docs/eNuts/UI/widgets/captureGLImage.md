## Overview & Design Context
`CaptureGLImage` subclasses `jAGQt.widgets.image.GLImage`. It displays stream frames like GLImage and additionally emits keyboard and mouse signals. It contains **no** recording state or inject logic. Coordinate mapping for inject uses inherited `mapToContent` / `contentSize` / `fittedRect` (same fit math as paint).

* **Design Decision / Deviation Notes:** Display-only regarding input policy. The KG Recorder **page** owns inject/log and calls `mapToContent` when handling mouse signals.

---

## Classes

### `CaptureGLImage`
- **Purpose:** GL stream host that surfaces key/mouse events for external handlers.
- **Signals:** `keyPressed`, `keyReleased`, `mousePressed`, `mouseMoved`, `mouseReleased` (each carries the Qt event object).
- **Inherited (GLImage):** `mapToContent`, `contentSize`, `fittedRect`, `presentExternal`, `fitMode`.
- **Methods:** Overrides key/mouse handlers to emit then call `super()`. Enables `StrongFocus` and mouse tracking; mouse press requests focus for subsequent keys.

## Sample Usage

```python
from eNuts.UI.widgets import CaptureGLImage

view = CaptureGLImage(bg="#1a1a1a")
view.keyPressed.connect(handler)
view.mousePressed.connect(handler)
# handler may call view.mapToContent(x, y) for fit-aware content pixels
```
