# Requirements & Design Specifications

## 1. Project Overview
Provide two focused image display widgets under jAGQt: a software path (Image) and an OpenGL path (GLImage). Both only display the image; interaction is optional and off by default so they can be used as pure display surfaces or as gesture-capture targets (e.g. CaptureImage).

## 2. Functional Requirements
- **FR-1:** Image must render via QWidget + cached scaled QPixmap only (no OpenGL).
- **FR-2:** GLImage must render via QOpenGLWidget (QPainter over GL context).
- **FR-3:** Both accept QPixmap | QImage | str (path) | Tensor | None for the image property.
- **FR-4:** Both support optional pan (left-drag), wheel zoom, and double-click reset when interactionEnabled is True.
- **FR-5:** When interactionEnabled is False (default), mouse/wheel events are not consumed so parent or subclass gesture handling works.
- **FR-6:** Public API (image, zoom, offset, interactionEnabled, onResize, onZoomChanged, resetView, setBackgroundColor) remains compatible for existing CaptureImage usage.

## 3. Non-Functional Requirements
- **NFR-1:** No external OpenGL bindings (PyOpenGL etc.); use only PySide6 OpenGL types.
- **NFR-2:** Prefer simplicity and single responsibility: Image = software display, GLImage = GPU display.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Combined backend removed
- **Affected Modules:** `src/jAGQt/widgets/Image/__image.py`, new `__glImage.py`
- **Description of Standard / Best Practice:** Single widget with a backend flag is common for optional GPU paths.
- **Divergence:** Backend flag and private _GLView child were removed. Two concrete classes are exported instead.
- **Design Decision & Justification:** The combined class became hard to reason about and maintain. Separating responsibilities keeps Image minimal (display only) and makes the OpenGL path explicit and independently testable.
- **Code Doc Cross-Reference:** See image.md and glImage.md.
