## Overview & Design Context

Policy implementation at `src/fluxCore/policy/__policy.py`.

An **array of images** is treated as **one process** and produces **one** action prediction. The model uses a proven MobileNetV3-Small backbone (ImageNet weights) and a custom head that scores against an embedded outcome registry via cosine similarity.

* **Design Decision / Deviation Notes:** Input is not a batch of independent images. It is a temporal/spatial array belonging to a single decision. See `requirement.md`.

---

## Classes

### `Policy`
- **Purpose:** Image-array → single discrete action key, via embedded registry scoring. Implements `iPolicy`.
- **Methods:**
  - `forward(imageArray)` → normalized embedding in registry space `[B, embedDim]`.
  - `score(embedding)` → cosine similarity scores against the registry `[B, numActions]`.
  - `predict(imageArray)` → action key string for one process.
  - `reset()` → no-op (stateless; kept for interface stability).
  - `device` (property) → current torch device.
  - `actionKeys` (property) → fixed vocabulary `("down", "up", "move", "inject")`.

---

## Functions

*(None — all behaviour lives on the `Policy` class.)*

---

## Constants & Globals

### `C_ACTION_KEYS`
- **Type:** `tuple[str, ...]`
- **Value / Description:** `("down", "up", "move", "inject")`

### `C_NUM_ACTIONS`
- **Type:** `int`
- **Value / Description:** `4`

### `C_DEFAULT_FEATURE_DIM`
- **Type:** `int`
- **Value / Description:** `512` — intermediate feature size after the backbone projection.

### `C_DEFAULT_IMAGE_SIZE`
- **Type:** `int`
- **Value / Description:** `224` — recommended spatial size when preparing frames for the pretrained backbone.

## Sample Usage

```python
from fluxCore.policy import Policy, C_ACTION_KEYS
import torch

# Registry: one embedding per action key
registry = torch.randn(len(C_ACTION_KEYS), 128)
policy = Policy(actionRegistryEmbeddings=registry, device="cpu")

# One process = array of T images, shape [T, 3, H, W]
imageArray = torch.rand(8, 3, 224, 224)

actionKey = policy.predict(imageArray)   # e.g. "down"
embedding = policy.forward(imageArray)   # [1, 128]
scores = policy.score(embedding)         # [1, 4]
```
