## Overview & Design Context
Software-only image display. Paint the image. Nothing else.
* **Design Decision / Deviation Notes:** No event handlers. No signals. Display only.

---

## Classes

### `Image`
- **Purpose:** Display an image. Accepts QPixmap, QImage, path string, or torch Tensor.
- **Methods:**
  - `setupUI()` -> Paint attributes and background.
  - `setBackgroundColor(color)` -> Fill color.
  - `resetView()` -> Fit image to widget (aspect-preserving) and center.
  - `paintEvent(event)` -> Draw background + scaled image.

---

## Sample Usage

```python
from jAGQt.widgets.image import Image

view = Image(bg="#1e1e1e")
view.image = "/path/to/frame.png"
```
