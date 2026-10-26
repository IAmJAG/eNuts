## Overview & Design Context
Software-only image display widget. Renders via QWidget + cached scaled QPixmap. Optional pan/zoom when interaction is enabled; when disabled (default) pointer events pass through for gesture capture.
* **Design Decision / Deviation Notes:** Split from the previous combined Image (software + OpenGL). Image is now purely software; OpenGL lives in GLImage.

---

## Classes

### `Image`
- **Purpose:** Display an image with optional interactive zoom/pan. Accepts QPixmap, QImage, path string, or torch Tensor.
- **Methods:**
  - `setupUI()` -> Configure paint attributes, mouse tracking, focus, and background.
  - `setBackgroundColor(color)` -> Set fill color used when no image or behind the image.
  - `resetView()` -> Fit image to widget (aspect-preserving) and center it.
  - `_rebuildScaled()` -> Rebuild the cached scaled pixmap from current zoom.
  - `_tensorToPixmap(tensor)` -> Convert torch Tensor (CHW/HWC, float or uint8) to QPixmap.
  - `paintEvent(event)` -> Fill background and draw the scaled image at current offset.
  - `wheelEvent` / `mousePressEvent` / `mouseMoveEvent` / `mouseReleaseEvent` / `mouseDoubleClickEvent` -> Optional interaction (gated by `interactionEnabled`).

---

## Sample Usage

```python
from jAGQt.widgets.image import Image

view = Image(bg="#1e1e1e")
view.image = "/path/to/frame.png"
view.interactionEnabled = False   # for CaptureImage-style gesture capture
```
