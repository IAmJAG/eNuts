# Requirements & Design Specifications

## 1. Project Overview

Minimal policy package under `src/fluxCore/policy/`.

The policy accepts a single image and produces one discrete action key.

Project-level requirements (including the deferred advanced features) live at `.docs/policy/requirement.md`. This document covers only the concrete package that has been implemented.

## 2. Functional Requirements

- **FR-1:** Accept a single image as `torch.Tensor` with shape `[C,H,W]` or `[B,C,H,W]`.
- **FR-2:** Produce one of the four action keys: `down`, `up`, `move`, `inject`.
- **FR-3:** Pre-process the image to a stable internal shape of 24×24×3 (resize, channel handling, simple [0,1] scaling).
- **FR-4:** Expose both a training-friendly `forward` (logits) and an inference helper `predict` (action key string).

## 3. Non-Functional Requirements

- **NFR-1:** The class implements the `iPolicy` protocol.
- **NFR-2:** Documentation follows path mirroring under `.docs/fluxCore/policy/`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Tiny CNN instead of MobileNetV3
- **Affected Modules:** `src/fluxCore/policy/__policy.py`
- **Description of Standard / Best Practice:** Many vision policies start from a pre-trained MobileNet or similar ImageNet backbone.
- **Divergence:** A three-layer CNN ending in adaptive average pooling is used.
- **Design Decision & Justification:** The locked internal resolution is 24×24. MobileNetV3-Small is designed for ~224×224; at 24×24 it loses almost all spatial signal. A purpose-built tiny network is more appropriate for the current minimal scope.
- **Code Doc Cross-Reference:** Reflected in `policy.md` and `implementation.md`.
