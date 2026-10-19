## Overview & Design Context

Policy implementation at `src/fluxCore/policy/__policy.py`.

An **array of images** is treated as **one process** and produces **one** action prediction. The model uses a proven MobileNetV3-Small backbone (ImageNet weights) and a custom head that scores against an embedded outcome registry via cosine similarity.

The **action vocabulary is volatile**. Registry size is not fixed by a compile-time constant. New actions can be added with `setRegistry` without rebuilding the backbone; fine-tuning is expected only for the change, not a full retrain. Older samples do not need re-annotation merely because the vocabulary grew.

---

## Classes

### `Policy`
- **Purpose:** Image-array → single discrete action key via embedded registry scoring. Implements `iPolicy`.
- **Methods:**
  - `forward(imageArray)` → normalized embedding `[B, embedDim]`.
  - `score(embedding)` → cosine scores against the **current** registry `[B, numActions]`.
  - `predict(imageArray)` → action key string from the current `actionKeys`.
  - `setRegistry(embeddings, actionKeys)` → replace/extend vocabulary without rebuilding the backbone.
  - `reset()` → no-op (stateless).
  - `device` / `actionKeys` / `numActions` (properties).

---

## Constants & Globals

### `C_SEED_ACTION_KEYS`
- **Type:** `tuple[str, ...]`
- **Value / Description:** `("down", "up", "move", "inject")` — optional seed only; not a hard limit.

### `C_DEFAULT_FEATURE_DIM` / `C_DEFAULT_IMAGE_SIZE`
- **Type:** `int`
- **Value / Description:** `512` / `224`

## Sample Usage

```python
from fluxCore.policy import Policy, C_SEED_ACTION_KEYS
import torch

keys = list(C_SEED_ACTION_KEYS)
registry = torch.randn(len(keys), 128)
policy = Policy(actionRegistryEmbeddings=registry, actionKeys=keys)

imageArray = torch.rand(8, 3, 224, 224)
print(policy.predict(imageArray))

# Vocabulary grows — no full retrain required by design
keys.append("scroll")
registry = torch.cat([registry, torch.randn(1, 128)], dim=0)
policy.setRegistry(registry, keys)
```
