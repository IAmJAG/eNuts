# Requirements & Design Specifications

## 1. Project Overview

This document defines the **minimal** policy for eNuts.

The policy accepts a single image and produces the next discrete action.

All previously discussed advanced features (intent, action history, continuous/variant arguments, temporal carousel, stride, dual heads, etc.) are deferred. They may be re-introduced later once the basic loop is working.

## 2. Functional Requirements

- **FR-1 (Input):** The policy accepts a single image as `ndarray` or `torch.Tensor`.
- **FR-2 (Output):** The policy produces the next discrete action key.
- **FR-3 (Action vocabulary):** The first version uses the following fixed registry:

```text
[
  { key: "down",   description: "finger/right mouse button down" },
  { key: "up",     description: "finger/right mouse button up" },
  { key: "move",   description: "finger/mouse move" },
  { key: "inject", description: "send key" }
]
```

- **FR-4 (Pre-processing):** The policy (or a thin helper) must resize / normalize the incoming image to a stable internal representation before the backbone runs.

## 3. Non-Functional Requirements

- **NFR-1:** Interfaces must be stable so the same model can be trained offline and loaded at runtime.
- **NFR-2:** Documentation must follow the path-mirroring and triad rules in `.kilocode/rules/Documentation.md`.

## 4. Locked Design Decisions (Minimal Version)

| Item | Decision |
|------|----------|
| Input | Single image (`ndarray` \| `Tensor`) |
| Output | Discrete action key (`"down"` \| `"up"` \| `"move"` \| `"inject"`) |
| Internal image shape | 24 × 24 × 3 (subject to change if the backbone needs more resolution) |
| Action registry | The four keys listed in FR-3 |
| Runtime owner | A simple Policy Wrapper that feeds one frame and receives one action key |

## 5. Explicitly Deferred

The following are **out of scope** for the current minimal policy:

- Intent
- Action / argument history
- Variant continuous arguments (box, coordinate, key, text)
- Temporal stack / carousel / stride
- Dual-head (action + parameter) prediction
- Humanization / micro-jitter
- Training data format details beyond “image → action” pairs

These may be added in later iterations once the basic image → action loop is proven.

## 6. Remaining Open Items (Minimal Scope)

- Exact pre-processing details (dtype, value range, normalization constants).
- Backbone choice (tiny CNN vs adapted MobileNetV3-Small at 24×24, etc.).
- How the discrete action is produced (classification head over the four keys).
- Package location under `src/` and corresponding documentation path.
- Training loop and data format for the minimal “image → action” case.
