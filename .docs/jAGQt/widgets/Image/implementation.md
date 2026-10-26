# Implementation Details

## 1. Architecture Overview
- `Image`: QWidget paint path only.
- `GLImage`: QOpenGLWidget paintGL path only.
- No event handlers, no signals on either class.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/Image/__image.py` | `.docs/jAGQt/widgets/Image/image.md` | Software image display |
| `src/jAGQt/widgets/Image/__glImage.py` | `.docs/jAGQt/widgets/Image/glImage.md` | OpenGL image display |

## 3. Core Workflows
1. Set `view.image`.
2. Normalized to QPixmap; `resetView()` fits and centers.
3. Image: dirty flag → rebuild scaled pixmap → paintEvent draws it.
4. GLImage: upload texture / fallback QImage → paintGL draws it.
