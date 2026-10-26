## Overview & Design Context
OpenGL image display. Paint the image. Nothing else.
* **Design Decision / Deviation Notes:** No event handlers. No signals. Display only.

---

## Classes

### `GLImage`
- **Purpose:** GPU-backed image display.
- **Methods:**
  - `setupUI()` -> Background.
  - `setBackgroundColor(color)` -> Clear color.
  - `resetView()` -> Fit and center.
  - `initializeGL` / `resizeGL` / `paintGL` -> Clear and draw.

---

## Sample Usage

```python
from jAGQt.widgets.image import GLImage

view = GLImage(bg="#1e1e1e")
view.image = some_qpixmap
```
