# Requirements & Design Specifications

## 1. Project Overview
eNuts UI widgets package: thin view surfaces for pages (capture hosts, spinners).

## 2. Functional Requirements
- **FR-1:** `CaptureImage` displays software-backed frames and emits key/mouse events.
- **FR-2:** `CaptureGLImage` displays OpenGL-backed frames (`presentExternal`) and emits the same key/mouse event set.
- **FR-3:** Capture hosts must not own recording session state; controllers subscribe to signals.

## 3. Non-Functional Requirements
- **NFR-1:** Keyboard focus must be obtainable on the GL surface so inject path receives keys.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: `Parallel CaptureImage / CaptureGLImage`
- **Affected Modules:** `eNuts/UI/widgets/__captureImage.py`, `eNuts/UI/widgets/__captureGLImage.py`
- **Description of Standard / Best Practice:** Single interactive image widget with backend switch.
- **Divergence:** Separate subclasses of Image vs GLImage matching the dual display stack.
- **Design Decision & Justification:** Image and GLImage do not share a common QWidget input base beyond ComponentBase; mirroring CaptureImage keeps OpenGL present path intact.
- **Code Doc Cross-Reference:** `captureImage.md`, `captureGLImage.md`
