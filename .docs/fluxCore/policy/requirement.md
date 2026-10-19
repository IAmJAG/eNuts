# Requirements & Design Specifications

## 1. Project Overview

Policy package under `src/fluxCore/policy/`.

The policy accepts an **array of images as one process** and produces **one** discrete action by scoring against an embedded outcome registry.

## 2. Functional Requirements

- **FR-1 (Input):** `[T, 3, H, W]` or `[B, T, 3, H, W]`.
- **FR-2 (Semantics):** One array → one prediction (frames are fused, not classified independently).
- **FR-3 (Backbone):** Proven pretrained model (MobileNetV3-Small). May be frozen.
- **FR-4 (Head):** Custom head maps fused features into registry embedding space.
- **FR-5 (Registry):** Cosine similarity against a **dynamic** embedded outcome registry. Size is not fixed at build time beyond the tensors supplied.
- **FR-6 (Volatile vocabulary):** Actions may be added over the life of the system. Extending the registry must not require re-annotating historical samples or retraining the entire network from scratch. Fine-tuning scoped to the change is acceptable.
- **FR-7 (Output):** `predict` returns a key from the **current** `actionKeys` list.

## 3. Non-Functional Requirements

- **NFR-1:** Implements `iPolicy`.
- **NFR-2:** Documentation under `.docs/fluxCore/policy/`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: No fixed action count
- **Affected Modules:** `src/fluxCore/policy/__policy.py`
- **Description of Standard / Best Practice:** Many classifiers bake `numClasses` into the final linear layer.
- **Divergence:** Outcome count comes only from the registry. `setRegistry` updates keys and rows; backbone and head geometry (aside from `embedDim`) stay put.
- **Design Decision & Justification:** Vocabulary changes during development and training. Full or broad re-fits are not feasible when data is limited or when older images must remain valid under their original labels.
- **Code Doc Cross-Reference:** `policy.md`, `implementation.md`.
