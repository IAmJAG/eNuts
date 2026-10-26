## Overview & Design Context
OpenGL-backed image display widget. Uses QOpenGLWidget with QPainter over the GL context (no fixed-function pipeline, no PyOpenGL). Same public surface as Image for image, zoom, offset, and interaction.
* **Design Decision / Deviation Notes:** Extracted from the previous combined Image backend path so Image stays software-only and simple.

---

## Classes

### `GLImage`
- **Purpose:** GPU-backed image display with the same optional pan/zoom behaviour as Image.
- **Methods:**
  - `setupUI()` -> Mouse tracking, focus, background.
  - `setBackgroundColor(color)` -> Clear color for the GL surface.
  - `resetView()` -> Fit and center.
  - `_uploadTexture(pixmap)` / `_clearTexture()` -> Manage QOpenGLTexture + fallback QImage.
  - `_tensorToPixmap(tensor)` -> Same Tensor conversion as Image.
  - `initializeGL` / `resizeGL` / `paintGL` -> Clear, scale, and draw via QPainter.
  - Interaction events gated by `interactionEnabled` (same contract as Image).

---

## Sample Usage

```python
from jAGQt.widgets.image import GLImage

view = GLImage(bg="#1e1e1e")
view.image = some_qpixmap
view.interactionEnabled = True
```
