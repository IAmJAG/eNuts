## Overview & Design Context
OpenGL image display. Shows the image and handles resize via ``fitMode``.

---

## Classes

### `GLImage`
- **Purpose:** GPU-backed image display. Same fit modes as Image.
- **Properties:**
  - `image` — QPixmap | QImage | str | Tensor | None
  - `fitMode` — ImageFitMode (Scale | Fill | Crop)
- **Methods:**
  - `setBackgroundColor(color)`
  - `initializeGL` / `resizeGL` / `paintGL` / `resizeEvent`

---

## Sample Usage

```python
from jAGQt.widgets.image import GLImage, ImageFitMode

view = GLImage(fitMode=ImageFitMode.Fill)
view.image = some_qpixmap
```
