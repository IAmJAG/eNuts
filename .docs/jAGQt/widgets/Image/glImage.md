## Overview & Design Context
OpenGL image display. Shows the image and handles resize via ``fitMode``. Live path uses ``presentExternal``. Public mapping helpers share the same Scale/Fill/Crop math as paint so inject/touch can hit the correct content pixels.

---

## Classes

### `GLImage`
- **Purpose:** GPU-backed image display. Same fit modes as Image.
- **Properties:**
  - `image` — QPixmap | QImage | str | None
  - `fitMode` — ImageFitMode (Scale | Fill | Crop)
  - `liveSeq` / `livePts` — last presented stream frame identity
- **Methods:**
  - `presentExternal(...)` / `clearPresent()` — live stream present path
  - `contentSize()` — last content (w, h)
  - `fittedRect()` — widget-space draw rect (letterbox etc.)
  - `mapToContent(x, y)` — widget → content pixels; `None` outside Scale bars
  - `mapToContentPoint(pos)` — QPointF variant
  - `setBackgroundColor(color)`
  - `initializeGL` / `resizeGL` / `paintGL` / `resizeEvent`

---

## Sample Usage

```python
from jAGQt.widgets.image import GLImage, ImageFitMode

view = GLImage(fitMode=ImageFitMode.Scale)
# after presentExternal / image set:
mapped = view.mapToContent(event.position().x(), event.position().y())
if mapped is not None:
    content_x, content_y = mapped
```
