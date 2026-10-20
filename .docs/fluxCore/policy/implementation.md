# Implementation Details

## 1. Architecture Overview

```text
imageArray [T,3,H,W] | [B,T,3,H,W]
        → backbone → projection → mean over T   (fused)
                ├─ actionHead → L2 norm → score vs registry → action key
                └─ argHead → Sigmoid → arguments [argDim]
```

## 2. Public vs internal

| Public | Internal |
| :--- | :--- |
| `forward`, `predict`, `setRegistry`, `actionKeys` | `_backbone`, `_projection`, `_actionHead`, `_argHead`, `_registry`, `_score`, `_fuse` |

## 3. Weights vs computation

| Change | Weights |
| :--- | :--- |
| Add actions (`setRegistry`, same embedDim) | Registry buffer only |
| Change `argDim` / `featDim` / embedDim | Head / proj shapes change |
