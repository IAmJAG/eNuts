## Overview & Design Context

Policy at `src/fluxCore/policy/__policy.py`.

One **array of images** = one process = **one action key + one argument vector**.

- Action: cosine score against a dynamic embedded registry (volatile vocabulary).
- Arguments: continuous vector in `[0, 1]` (default length 4) for spatial payload.

---

## Classes

### `Policy`
- **Purpose:** Image-array → `(actionKey, arguments)`. Implements `iPolicy`.
- **Public:**
  - `forward(imageArray)` → `(actionEmbedding [B, embedDim], arguments [B, argDim])`
  - `predict(imageArray)` → `(actionKey: str, arguments: Tensor[argDim])`
  - `setRegistry(actRegEmbeddings, actKeys)` → update vocabulary
  - `actionKeys` → current vocabulary
- **Not public:** backbone, heads, registry, `_score`, `_fuse`.

---

## Constants

### `C_SEED_ACTION_KEYS`
Seed labels only — not a fixed vocabulary size.

### `C_DEFAULT_FEATURE_DIM`
`512`

### `C_DEFAULT_ARG_DIM`
`4` — layout: `[x|left, y|top, width, height]` (normalized). Coordinate-style actions use the first two values.

## Sample Usage

```python
from fluxCore.policy import Policy, C_SEED_ACTION_KEYS
import torch

keys = list(C_SEED_ACTION_KEYS)
registry = torch.randn(len(keys), 128)
policy = Policy(actRegEmbeddings=registry, actKeys=keys)

imageArray = torch.rand(8, 3, 224, 224)
actionKey, args = policy.predict(imageArray)
# args: tensor of shape [4], values in [0, 1]
```
