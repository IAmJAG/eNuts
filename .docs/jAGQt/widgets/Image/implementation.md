# Implementation Details

## 1. Architecture Overview
- `ImageFitMode` enum: Scale, Fill, Crop.
- `Image` / `GLImage`: hold image + fitMode; on dirty (set image / resize / change mode) recompute draw pixmap/image and rect; paint only.
- Image input: QPixmap, QImage, path str, or None. No Tensor.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/Image/__fitMode.py` | — | ImageFitMode enum |
| `src/jAGQt/widgets/Image/__image.py` | `.docs/jAGQt/widgets/Image/image.md` | Software display |
| `src/jAGQt/widgets/Image/__glImage.py` | `.docs/jAGQt/widgets/Image/glImage.md` | OpenGL display |

## 3. Core Workflows
1. Set `image` or `fitMode` or widget resizes → mark dirty.
2. On paint: if dirty, `_recompute()` builds scaled pixmap/image + draw rect from fitMode.
3. Paint draws background then the prepared image into the draw rect.
