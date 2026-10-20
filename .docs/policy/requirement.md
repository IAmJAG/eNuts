# Requirements & Design Specifications

## 1. Project Overview

Policy for eNuts: an **array of images** is one process and yields **one action key plus arguments**.

**Implementation:** `src/fluxCore/policy/`

## 2. Functional Requirements

- **FR-1:** Input `[T, 3, H, W]` or `[B, T, 3, H, W]`.
- **FR-2:** One prediction per array (fused frames).
- **FR-3:** MobileNetV3-Small backbone, optional freeze.
- **FR-4:** Action via cosine similarity on a dynamic registry (volatile vocabulary).
- **FR-5:** Arguments via a continuous vector (default 4-D, normalized `[0, 1]`).
- **FR-6:** `predict` → `(actionKey, arguments)`.

## 3. Locked Decisions

| Item | Decision |
|------|----------|
| Input | Array of images = one process |
| Action | Registry scoring; count not fixed |
| Arguments | Shared continuous head; layout interpreted by action key |
| Package | `src/fluxCore/policy/` |

## 4. Deferred

- Typed variant args (key/text branches), intent, history, LSTM fusion, training packaging
