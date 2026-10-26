# Requirements & Design Specifications

## 1. Project Overview
Provide two focused image display widgets under jAGQt: a software path (Image) and an OpenGL path (GLImage). Both are display-only. No pan, zoom, or mouse interaction.

## 2. Functional Requirements
- **FR-1:** Image must render via QWidget + cached scaled QPixmap only (no OpenGL).
- **FR-2:** GLImage must render via QOpenGLWidget (QPainter over GL context).
- **FR-3:** Both accept QPixmap | QImage | str (path) | Tensor | None for the image property.
- **FR-4:** Both fit and center the image on set and on resize (resetView).
- **FR-5:** No interaction handling (no wheel, drag, double-click) in either widget.
- **FR-6:** CaptureImage subclasses Image and adds event emission only.

## 3. Non-Functional Requirements
- **NFR-1:** No external OpenGL bindings; use only PySide6 OpenGL types.
- **NFR-2:** Single responsibility: display the image. Nothing else.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Interaction removed
- **Affected Modules:** `src/jAGQt/widgets/Image/__image.py`, `__glImage.py`, `src/eNuts/UI/widgets/__captureImage.py`
- **Description of Standard / Best Practice:** Interactive viewers often embed pan/zoom in the widget.
- **Divergence:** All interaction code was stripped. Display only.
- **Design Decision & Justification:** Explicit request: rebase so the widget only displays the image. Interaction belongs elsewhere (or in subclasses that need it).
- **Code Doc Cross-Reference:** See image.md and glImage.md.
