# Requirements & Design Specifications

## 1. Project Overview

Policy under `src/fluxCore/policy/`: array of images → **action key + arguments**.

## 2. Functional Requirements

- **FR-1:** Input `[T, 3, H, W]` or `[B, T, 3, H, W]`.
- **FR-2:** One prediction per array (frames fused).
- **FR-3:** Proven backbone (MobileNetV3-Small), optional freeze.
- **FR-4:** Action via cosine score on a dynamic embedded registry.
- **FR-5:** Volatile action vocabulary (`setRegistry`); no fixed action count.
- **FR-6 (Arguments):** Also emit a continuous argument vector (default dim 4, values in `[0, 1]`) for spatial payload (coordinate / box fields).
- **FR-7:** `predict` returns `(actionKey, arguments)`.

## 3. Design Decisions

### Dual head
- Shared fused visual features.
- Action head → registry embedding space.
- Argument head → sigmoid-normalized vector (does not grow when vocabulary grows).

### Argument layout (default)
`[x or left, y or top, width, height]` in normalized screen space. Downstream code interprets fields based on the chosen action key.
