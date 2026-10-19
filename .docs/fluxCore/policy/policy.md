## Overview & Design Context

Policy at `src/fluxCore/policy/__policy.py`.

One **array of images** = one process = one action, scored against a dynamic embedded registry.

Public surface is intentionally small.

---

## Classes

### `Policy`
- **Purpose:** Image-array → action key via registry scoring. Implements `iPolicy`.
- **Public methods / properties:**
  - `forward(imageArray)` → embedding `[B, embedDim]`
  - `predict(imageArray)` → action key `str`
  - `setRegistry(embeddings, actionKeys)` → update volatile vocabulary
  - `actionKeys` → current vocabulary tuple
  - `reset()` → no-op (interface stability)
- **Not public:** backbone, head, registry buffer, `_score`, device helpers, `numActions`.

---

## Constants

### `C_SEED_ACTION_KEYS`
Optional seed labels `("down", "up", "move", "inject")` — not a fixed vocabulary size.

### `C_DEFAULT_FEATURE_DIM`
Default intermediate feature size (`512`).

## Sample Usage

```python
from fluxCore.policy import Policy, C_SEED_ACTION_KEYS
import torch

keys = list(C_SEED_ACTION_KEYS)
registry = torch.randn(len(keys), 128)
policy = Policy(actionRegistryEmbeddings=registry, actionKeys=keys)

imageArray = torch.rand(8, 3, 224, 224)
key = policy.predict(imageArray)
```
