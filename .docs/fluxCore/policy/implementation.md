# Implementation Details

## 1. Architecture Overview

```text
imageArray [T, 3, H, W]  or  [B, T, 3, H, W]
        |
        v
  MobileNetV3-Small (optional freeze) → [B*T, 576]
        |
        v
  proj → [B, T, featureDim] → mean over T → [B, featureDim]
        |
        v
  head → L2-normalize → [B, embedDim]
        |
        +-- score vs dynamic registry [numActions, embedDim]
        +-- predict → actionKeys[argmax]
```

`numActions` is always `registry.size(0)`. It is not a module constant.

## 2. Vocabulary growth

```text
setRegistry(newEmbeddings, newKeys)
  - requires same embedDim as the existing head
  - replaces _registry buffer and _actionKeys
  - does not rebuild backbone or head layers
```

Expected operational pattern when a new action appears:

1. Append a new embedding row (and key).
2. Call `setRegistry`.
3. Fine-tune only what is needed (often head + new row), not the full historical dataset under new labels.

Historical samples keep their original action labels; they are not invalidated by vocabulary growth.

## 3. Directory & Module Mapping

| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/policy/__policy.py` | `.docs/fluxCore/policy/policy.md` | Policy class |
| `src/fluxCore/policy/__init__.py` | — | Public exports |
| `src/fluxCore/types/interface/policy/__policy.py` | — | `iPolicy` |
