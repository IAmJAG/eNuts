# Requirements & Design Specifications

## 1. Project Overview

Minimal policy for eNuts.

The policy accepts an **array of images as one process** and produces **one** discrete action by scoring against an embedded outcome registry.

**Implementation:** `src/fluxCore/policy/`

## 2. Functional Requirements

- **FR-1 (Input):** Array of images `[T, 3, H, W]` (one process) or `[B, T, 3, H, W]` (batch of processes).
- **FR-2 (Output):** One discrete action key per array: `down` | `up` | `move` | `inject`.
- **FR-3 (Backbone):** Proven pretrained model (MobileNetV3-Small) with optional freeze.
- **FR-4 (Head + registry):** Custom head projects into an embedded outcome registry; prediction is cosine nearest neighbour.

## 3. Locked Design Decisions

| Item | Decision |
|------|----------|
| Input semantics | Array of images = one process → one result |
| Backbone | MobileNetV3-Small (ImageNet weights) |
| Prediction | Cosine similarity vs embedded action registry |
| Action vocabulary | `down`, `up`, `move`, `inject` |
| Package | `src/fluxCore/policy/` |
| Interface | `iPolicy` |

## 4. Explicitly Deferred

- Intent conditioning
- Explicit action/argument history input
- Continuous / variant argument heads
- Learned temporal fusion beyond mean pool (LSTM/attention)
- Training loop and dataset packaging
- Checkpoint helpers

## 5. Remaining Open Items

- How action registry embeddings are constructed and versioned
- Preferred frame count `T` and preprocessing (exact normalize constants)
- Training procedure and loss
