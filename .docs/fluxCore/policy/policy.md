## Overview & Design Context

Policy at `src/fluxCore/policy/__policy.py`, options at `__policyOptions.py`.

Construction is **only** via `PolicyOptions` (action / key / text registries with embeddings, arg kinds, feature dim, freeze, device).

---

## Classes

### `RegistryOptions`
- **Purpose:** One discrete registry: `embeddings` `[N, embedDim]` + `labels`.

### `PolicyOptions`
- **Purpose:** Full construction blob for `Policy`.
- **Fields:** `action` (required), `key` / `text` (optional), `argKinds`, `featureDim`, `freezeBackbone`, `device`.

### `Policy`
- **Public:** `forward`, `predict`, `actionKeys`
- **Init:** `Policy(options: PolicyOptions)` only

## Sample Usage

```python
from fluxCore.policy import (
    Policy, PolicyOptions, RegistryOptions, C_SEED_ACTION_KEYS
)
import torch

action = RegistryOptions(
    embeddings=torch.randn(4, 128),
    labels=list(C_SEED_ACTION_KEYS),
)
key = RegistryOptions(
    embeddings=torch.randn(3, 128),
    labels=["A", "TAB", "ESCAPE"],
)
text = RegistryOptions(
    embeddings=torch.randn(2, 128),
    labels=["login", "submit"],
)

options = PolicyOptions(action=action, key=key, text=text, device="cpu")
policy = Policy(options)

actionKey, argument = policy.predict(imageArray)
```
