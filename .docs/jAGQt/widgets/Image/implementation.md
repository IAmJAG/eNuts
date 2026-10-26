# Implementation Details

## 1. Architecture Overview
- `ImageBase` mixin: shared state and API (image, fitMode, background, dirty, drawRect).
- `Image` / `GLImage`: inherit ImageBase; own paint path and fit recompute buffers.
- `ImageFitMode`: Scale, Fill, Crop.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/Image/__fitMode.py` | — | ImageFitMode enum |
| `src/jAGQt/widgets/Image/__imageBase.py` | — | Shared mixin |
| `src/jAGQt/widgets/Image/__image.py` | `.docs/jAGQt/widgets/Image/image.md` | Software display |
| `src/jAGQt/widgets/Image/__glImage.py` | `.docs/jAGQt/widgets/Image/glImage.md` | OpenGL display |

## 3. Shared attributes (ImageBase)
| Attribute / API | Role |
| :--- | :--- |
| `_image` | Source QPixmap |
| `_backgroundColor` | Fill / clear color |
| `_fitMode` | Scale / Fill / Crop |
| `_drawRect` | Destination rect for paint |
| `_dirty` | Layout needs recompute |
| `fitMode` | Property |
| `image` | Property (str / QImage / QPixmap / None) |
| `setBackgroundColor` | Setter |
| `_toPixmap` | Input conversion |
| `_markDirty` | Dirty + update |
| `_onImageCleared` / `_onImageSet` | Subclass hooks |

## 4. Core Workflows
1. Set `image` or `fitMode` or resize → `_markDirty`.
2. On paint: if dirty, subclass `_recompute()` fills its buffer + `_drawRect`.
3. Paint draws background then buffer into `_drawRect`.
