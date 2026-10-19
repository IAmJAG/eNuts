# Implementation Details

## 1. Architecture Overview

```text
imageArray [T,3,H,W] | [B,T,3,H,W]
        → backbone → proj → mean over T → head → L2 norm
        → _score vs _registry → predict → actionKeys[index]
```

## 2. Public vs internal

| Public | Internal |
| :--- | :--- |
| `forward`, `predict`, `setRegistry`, `actionKeys`, `reset` | `_backbone`, `_proj`, `_head`, `_registry`, `_score`, `_device`, `_embedDim`, `_freezeBackbone` |

`train()` is overridden only to keep a frozen backbone in eval mode; callers still use the normal `nn.Module` training API.

## 3. Vocabulary growth

`setRegistry` requires the same `embedDim`. It does not rebuild weight-bearing layers.
