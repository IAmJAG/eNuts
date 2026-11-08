# Requirements & Design Specifications

## 1. Project Overview
eNuts UI widgets package: thin view surfaces for pages (stream canvas, spinners).

## 2. Functional Requirements
- **FR-1:** Stream display uses `jAGQt.widgets.Canvas` / `GLCanvas` (not eNuts Capture* wrappers).
- **FR-2:** `GLCanvas` / `Canvas` emit key/mouse signals for inject controllers.
- **FR-3:** Canvas hosts must not own recording session state; controllers subscribe to signals.
- **FR-4:** Live path implements `iFrameView.present` / `clear` on the canvas.

## 3. Non-Functional Requirements
- **NFR-1:** Keyboard focus must be obtainable on the GL surface so inject path receives keys.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Capture* removed
- **Affected Modules:** former `eNuts/UI/widgets/__captureImage.py`, `__captureGLImage.py`
- **Description of Standard / Best Practice:** Single interactive canvas API under jAGQt.
- **Divergence:** Capture* subclasses deleted; input signals live on `Canvas` / `GLCanvas`.
- **Design Decision & Justification:** Avoid parallel Image/Capture stacks; rename Image→Canvas package is the sole display host.
- **Code Doc Cross-Reference:** jAGQt Canvas package; `kgRecorderPage.md`
