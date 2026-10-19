# Requirements & Design Specifications

## 1. Project Overview

Policy for eNuts: an **array of images** is one process and yields **one** discrete action via an embedded outcome registry.

**Implementation:** `src/fluxCore/policy/`

## 2. Functional Requirements

- **FR-1:** Input `[T, 3, H, W]` or `[B, T, 3, H, W]`.
- **FR-2:** One prediction per array (fused frames).
- **FR-3:** Proven backbone (MobileNetV3-Small), optional freeze.
- **FR-4:** Custom head + cosine score against a **dynamic** registry.
- **FR-5 (Volatile vocabulary):** Action set may grow. Extending the registry must not force full retrain or re-annotation of older data. Scoped fine-tuning for the change is expected.

## 3. Locked Design Decisions

| Item | Decision |
|------|----------|
| Input semantics | Array of images = one process → one result |
| Backbone | MobileNetV3-Small (ImageNet weights) |
| Prediction | Cosine similarity vs registry |
| Action count | **Not fixed** — registry + `actionKeys` are authoritative |
| Vocabulary updates | `setRegistry`; backbone not rebuilt |
| Package | `src/fluxCore/policy/` |

## 4. Deferred

- Intent, history, continuous argument heads
- Learned temporal fusion beyond mean pool
- Training loop / checkpoint packaging

## 5. Open

- How new registry rows are initialized when an action is added
- Fine-tune recipe when vocabulary grows
- Preferred `T` and exact image normalization
