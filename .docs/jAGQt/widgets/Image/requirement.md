# Requirements & Design Specifications

## 1. Project Overview
Image and GLImage display an image and handle resize. No interaction, no extra features.

## 2. Functional Requirements
- **FR-1:** Image — software QWidget paint path.
- **FR-2:** GLImage — QOpenGLWidget paint path.
- **FR-3:** Accept QPixmap | QImage | str | Tensor | None.
- **FR-4:** Fit modes:
  - Scale — proportional fit inside widget.
  - Fill — stretch to fill widget.
  - Crop — proportional cover, center crop.
- **FR-5:** On resize, recompute layout from fitMode and redraw.

## 3. Non-Functional Requirements
- **NFR-1:** Display and resize only.
