## Overview & Design Context
Software-only image display widget. Renders via QWidget + cached scaled QPixmap. Display only — no pan, zoom, or mouse interaction.
* **Design Decision / Deviation Notes:** Split from the previous combined Image. Image is purely software and display-only; OpenGL lives in GLImage. All interaction code removed.

---

## Classes

### `Image`
- **Purpose:** Display an image. Accepts QPixmap, QImage, path string, or torch Tensor. Fits and centers on set/resize.
- **Methods:**
  - `setupUI()` -> Configure paint attributes and background.
  - `setBackgroundColor(color)` -> Set fill color.
  - `resetView()` -> Fit image to widget (aspect-preserving) and center.
  - `_rebuildScaled()` -> Rebuild the cached scaled pixmap from current zoom.
  - `_tensorToPixmap(tensor)` -> Convert torch Tensor to QPixmap.
  - `paintEvent(event)` -> Fill background and draw the scaled image at current offset.
  - `resizeEvent(event)` -> Emit onResize and re-fit.

---

## Sample Usage

```python
from jAGQt.widgets.image import Image

view = Image(bg="#1e1e1e")
view.image = "/path/to/frame.png"
```
