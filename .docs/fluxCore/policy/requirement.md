# Requirements & Design Specifications

## 1. Project Overview

Policy package under `src/fluxCore/policy/`.

The policy accepts an **array of images as one process** and produces **one** discrete action by scoring against an embedded outcome registry.

## 2. Functional Requirements

- **FR-1 (Input):** Accept an array of images shaped `[T, 3, H, W]` (one process) or `[B, T, 3, H, W]` (batch of processes).
- **FR-2 (Semantics):** The array is a single coherent unit. The model must fuse the T frames and emit one prediction per array, not one prediction per frame.
- **FR-3 (Backbone):** Use a proven pretrained model (MobileNetV3-Small, ImageNet weights). The backbone may be frozen.
- **FR-4 (Head):** Own classification / projection head that maps the fused representation into the embedding space of the outcome registry.
- **FR-5 (Registry):** Predict by cosine similarity against an immutable embedded outcome registry. The registry order matches `C_ACTION_KEYS`.
- **FR-6 (Output):** `predict` returns one of `"down"`, `"up"`, `"move"`, `"inject"`.

## 3. Non-Functional Requirements

- **NFR-1:** Implements `iPolicy`.
- **NFR-2:** Documentation follows path mirroring under `.docs/fluxCore/policy/`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Array-of-images vs batch-of-images
- **Affected Modules:** `src/fluxCore/policy/__policy.py`
- **Description of Standard / Best Practice:** Many classifiers take `[B, 3, H, W]` and emit B independent labels.
- **Divergence:** Input is `[T, 3, H, W]` (or batched `[B, T, 3, H, W]`). T frames belong to one process and yield one label.
- **Design Decision & Justification:** Matches the product requirement that a short sequence of frames constitutes a single decision context.
- **Code Doc Cross-Reference:** `policy.md`, `implementation.md`.

### Issue / Item 2: Embedded registry instead of a plain linear classifier
- **Affected Modules:** `src/fluxCore/policy/__policy.py`
- **Description of Standard / Best Practice:** Final linear layer with `numClasses` logits + cross-entropy.
- **Divergence:** Head projects into an embedding space; prediction is nearest-neighbour (cosine) against a registry of action embeddings.
- **Design Decision & Justification:** Keeps the outcome space explicit and swappable; aligns with later hybrid discrete-continuous plans.
- **Code Doc Cross-Reference:** `policy.md`, `implementation.md`.
