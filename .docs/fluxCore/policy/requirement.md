# Requirements & Design Specifications

## 1. Project Overview

Minimal policy package under `src/fluxCore/policy/`.

The policy accepts a single image and produces one discrete action key.

Project-level requirements (including the deferred advanced features) live at `.docs/policy/requirement.md`. This document covers only the concrete package that has been implemented.

## 2. Functional Requirements

- **FR-1:** Accept a single image as `torch.Tensor` with shape `[C,H,W]` or `[B,C,H,W]` (any spatial size).
- **FR-2:** Produce one of the four action keys: `down`, `up`, `move`, `inject`.
- **FR-3:** The backbone must produce a fixed **24 × 24 × 3** feature map (the CNN result). This is not the input resolution.
- **FR-4:** Expose both a training-friendly `forward` (logits) and an inference helper `predict` (action key string). Also expose `extractFeatures` for the raw CNN result.

## 3. Non-Functional Requirements

- **NFR-1:** The class implements the `iPolicy` protocol.
- **NFR-2:** Documentation follows path mirroring under `.docs/fluxCore/policy/`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: 24×24×3 is the CNN result, not the input size
- **Affected Modules:** `src/fluxCore/policy/__policy.py`
- **Description of Standard / Best Practice:** Many pipelines resize the input image to a fixed size before the backbone.
- **Divergence:** Input spatial size is left free. The backbone itself (via strided convolutions + AdaptiveAvgPool) is responsible for emitting a 24×24×3 feature map.
- **Design Decision & Justification:** Matches the clarified requirement that 24×24×3 describes the CNN output, not the input.
- **Code Doc Cross-Reference:** Reflected in `policy.md` and `implementation.md`.
