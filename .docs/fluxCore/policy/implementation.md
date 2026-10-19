# Implementation Details

## 1. Architecture Overview

```text
imageArray [T, 3, H, W]  or  [B, T, 3, H, W]
        |
        |  reshape to [B*T, 3, H, W]
        v
  MobileNetV3-Small backbone (ImageNet weights)
  AdaptiveAvgPool + Flatten → [B*T, 576]
        |
        v
  Linear 576 → featureDim
        |
        |  reshape to [B, T, featureDim]
        v
  Fuse over T (mean) → [B, featureDim]
        |
        v
  Own head → embedDim, L2-normalize
        |
        +-- forward()  → embedding [B, embedDim]
        +-- score()    → cosine vs registry [B, numActions]
        +-- predict()  → action key string
```

The model is stateless. `reset()` exists only for `iPolicy` compatibility.

## 2. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/policy/__policy.py` | `.docs/fluxCore/policy/policy.md` | Policy class |
| `src/fluxCore/policy/__init__.py` | — | Public exports |
| `src/fluxCore/types/interface/policy/__policy.py` | — | `iPolicy` protocol |

## 3. Core Workflows & Data Flow

**Preparing one process (array of images)**
1. Load T raw frames (any realistic resolution).
2. Resize each to the backbone’s preferred size (typically 224×224).
3. Convert to float tensors, apply ImageNet normalization if desired.
4. Stack to `[T, 3, H, W]`.
5. Call `policy.predict(imageArray)` → one action key.

**Inference inside the model**
1. Ensure batch dimension → `[B, T, 3, H, W]`.
2. Flatten T into the batch, run backbone, project.
3. Restore `[B, T, featureDim]`, mean-pool over T.
4. Project into registry space, L2-normalize.
5. Cosine similarity against the registered action embeddings; argmax → key.

**Training (not yet packaged)**
- `forward` returns embeddings; `score` returns logits suitable for cross-entropy against action indices, or a contrastive loss against registry rows.
