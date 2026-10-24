## Overview & Design Context
`CaptureImage` subclasses `jAGQt.widgets.image.Image`. It displays frames exactly like Image and additionally emits keyboard and mouse signals. It contains **no** recording state or conditional filters.

* **Design Decision / Deviation Notes:** Keeps capture surface dumb so `KGRecorder` owns all session logic outside the Page.

---

## Classes

### `CaptureImage`
- **Purpose:** Plain stream host that surfaces key/mouse events.
- **Signals:** `keyPressed`, `keyReleased`, `mousePressed`, `mouseMoved`, `mouseReleased` (each carries the Qt event object).
- **Methods:** Overrides key/mouse event handlers to emit then call `super()` so normal Image behaviour (pan/zoom) remains.

## Sample Usage

```python
from eNuts.UI.widgets import CaptureImage

view = CaptureImage(bg="#1a1a1a", backend="software")
view.keyPressed.connect(handler)
```
