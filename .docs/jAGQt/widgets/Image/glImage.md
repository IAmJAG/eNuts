## Overview & Design Context
OpenGL-backed image display widget. Uses QOpenGLWidget with QPainter over the GL context. Display only — no pan, zoom, or mouse interaction.
* **Design Decision / Deviation Notes:** Extracted from the previous combined Image. All interaction code removed.

---

## Classes

### `GLImage`
- **Purpose:** GPU-backed image display. Same display contract as Image (fit/center on set/resize).
- **Methods:**
  - `setupUI()` -> Background.
  - `setBackgroundColor(color)` -> Clear color for the GL surface.
  - `resetView()` -> Fit and center.
  - `_uploadTexture(pixmap)` / `_clearTexture()` -> Manage QOpenGLTexture + fallback QImage.
  - `_tensorToPixmap(tensor)` -> Same Tensor conversion as Image.
  - `initializeGL` / `resizeGL` / `paintGL` -> Clear and draw via QPainter.
  - `resizeEvent(event)` -> Emit onResize and re-fit.

---

## Sample Usage

```python
from jAGQt.widgets.image import GLImage

view = GLImage(bg="#1e1e1e")
view.image = some_qpixmap
```
