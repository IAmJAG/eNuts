## Overview & Design Context

`PolicyOptions` reads known option keys from a shared `kwargs` dict and leaves the rest for `nn.Module`.

* **Design Decision / Deviation Notes:** `featureDimension` is always taken from the backbone. A supplied value is popped and ignored.

---

## Classes

### `PolicyOptions`
- **Purpose:** Holds policy hyperparameters and is serializable via `Properties`.
- **Methods:**
  - `__init__(module=None, kwargs=None)` → walks `DEFAULTS`, pops each known key, sets `_{key}`, and records it in `Properties`.
  - Properties: `freezeBackbone`, `featureDimension`, `intentEmbeddingDimension`, `actionEmbeddingDimension`, `parameterKindEmbeddingDimension`, `spatialEmbeddingDimension`, `spatialOutputDimension`, `frameSize`, `stackSize`, `normalizeMean`, `normalizeStd`.

---

## Functions

None.

---

## Constants & Globals

### `DEFAULTS`
- **Type:** `Dict[str, Any]`
- **Value / Description:** Default values for every option the class understands. Keys without a property are skipped.

## Sample Usage

```python
from fluxCore.policy import DCPolicy

policy = DCPolicy(stackSize=16, frameSize=224, freezeBackbone=True)
print(policy.options.stackSize, policy.options.frameSize)
```
