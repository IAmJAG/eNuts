# Requirements & Design Specifications

## 1. Project Overview
Image and GLImage are pure display widgets. Set an image, paint it. No event handling, no signals, no interaction.

## 2. Functional Requirements
- **FR-1:** Image renders via QWidget + cached scaled QPixmap.
- **FR-2:** GLImage renders via QOpenGLWidget + QPainter over GL.
- **FR-3:** Both accept QPixmap | QImage | str | Tensor | None.
- **FR-4:** Both provide resetView() to fit and center.
- **FR-5:** No event overrides other than the paint path required to draw.
- **FR-6:** CaptureImage subclasses Image and is responsible for its own event emission.

## 3. Non-Functional Requirements
- **NFR-1:** Single responsibility: display the image.
