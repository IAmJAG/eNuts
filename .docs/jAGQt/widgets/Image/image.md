## Overview & Design Context
Software image display. Shows the image and handles resize via ``fitMode``.

---

## Classes

### `Image`
- **Purpose:** Display an image. Resize behaviour controlled by ``fitMode``.
- **Properties:**
  - `image` — QPixmap | QImage | str | None
  - `fitMode` — ImageFitMode (Scale | Fill | Crop)
- **Methods:**
  - `setBackgroundColor(color)`
  - `paintEvent` / `resizeEvent` — recompute layout and draw

### `ImageFitMode`
- **Scale** — scale proportionally to fit inside the widget (letterbox).
- **Fill** — stretch to fill the entire widget (aspect ignored).
- **Crop** — scale proportionally to cover, center, crop to viewport.

---

## Sample Usage

```python
from jAGQt.widgets.image import Image, ImageFitMode

view = Image(bg="#1e1e1e", fitMode=ImageFitMode.Crop)
view.image = "/path/to/frame.png"
view.fitMode = ImageFitMode.Scale
```
