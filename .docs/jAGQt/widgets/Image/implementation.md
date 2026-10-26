# Implementation Details

## 1. Architecture Overview
- `Image` (QWidget + ComponentBase): software paint path, dirty-flag scaled pixmap cache.
- `GLImage` (QOpenGLWidget + ComponentBase): texture upload + QPainter draw in paintGL.
- Both share the same interaction contract (interactionEnabled default False) and the same image-input conversion (including Tensor).

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/Image/__image.py` | `.docs/jAGQt/widgets/Image/image.md` | Software image display |
| `src/jAGQt/widgets/Image/__glImage.py` | `.docs/jAGQt/widgets/Image/glImage.md` | OpenGL image display |
| `src/jAGQt/widgets/Image/__init__.py` | — | Exports Image, GLImage |

## 3. Core Workflows & Data Flow
1. Caller sets `view.image = value` (path / QImage / QPixmap / Tensor / None).
2. Value is normalized to QPixmap; view resets to fit-to-widget and centers.
3. Image: marks dirty, rebuilds scaled pixmap on paint, draws at offset.
4. GLImage: uploads RGBA texture / keeps fallback QImage, draws scaled in paintGL.
5. If interactionEnabled: wheel adjusts zoom about cursor; drag pans offset; double-click calls resetView.
