# Implementation Details

## 1. Architecture Overview

```text
image [B,C,H,W] or [C,H,W]
        |
        v
  _preprocess  (resize -> 24x24, float32, [0,1], 3-channel)
        |
        v
  tiny CNN backbone
    Conv 3->16 -> ReLU -> MaxPool
    Conv 16->32 -> ReLU -> MaxPool
    Conv 32->64 -> ReLU -> AdaptiveAvgPool(1x1) -> Flatten
        |
        v
  Linear(64 -> 4) logits
        |
        +-- forward()  -> logits
        +-- predict()  -> argmax -> action key string
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
1. Caller supplies an image tensor.
2. `predict(image)` runs pre-process + forward + argmax.
3. Returns one of `"down"`, `"up"`, `"move"`, `"inject"`.

**Training**
1. Caller supplies image batch and target action indices.
2. `forward(image)` returns logits.
3. Standard cross-entropy can be applied against the four-class target.

No training loop is provided in this package yet.
