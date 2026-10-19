# Implementation Details

## 1. Architecture Overview

```text
image [B,C,H,W] or [C,H,W]   (any spatial size)
        |
        v
  _preprocess  (float32, 3-channel, optional /255)
        |
        v
  backbone (CNN)
    Conv stride-2 blocks + 1x1 projection
    AdaptiveAvgPool2d -> [B, 3, 24, 24]     <--- CNN result
        |
        v
  head
    Flatten (1728) -> Linear 128 -> ReLU -> Linear 4
        |
        +-- extractFeatures() -> [B, 3, 24, 24]
        +-- forward()         -> logits [B, 4]
        +-- predict()         -> action key string
```

The model is intentionally stateless. `reset()` exists only to satisfy the `iPolicy` protocol.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/policy/__policy.py` | `.docs/fluxCore/policy/policy.md` | Minimal Policy class |
| `src/fluxCore/policy/__init__.py` | — | Public exports |
| `src/fluxCore/types/interface/policy/__policy.py` | — | `iPolicy` protocol |

## 3. Core Workflows & Data Flow

**Inference**
1. Caller supplies an image tensor (any spatial size).
2. `predict(image)` runs pre-process → backbone (→ 24×24×3) → head → argmax.
3. Returns one of `"down"`, `"up"`, `"move"`, `"inject"`.

**Training**
1. Caller supplies image batch and target action indices.
2. `forward(image)` returns logits.
3. Standard cross-entropy can be applied against the four-class target.

No training loop is provided in this package yet.
