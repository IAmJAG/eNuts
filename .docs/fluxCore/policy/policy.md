## Overview & Design Context

Minimal policy implementation located at `src/fluxCore/policy/__policy.py`.

Accepts a single image (any reasonable spatial size) and returns one discrete action key from the fixed vocabulary: `down`, `up`, `move`, `inject`.

* **Design Decision / Deviation Notes:** The backbone produces a fixed **24 × 24 × 3 feature map** (the CNN result). This is *not* the input resolution. Input images are only lightly normalized; the network itself is responsible for reaching the 24×24×3 representation. Advanced features (intent, history, continuous arguments, temporal stack) remain deferred.

---

## Classes

### `Policy`
- **Purpose:** Minimal image-to-action model. Implements `iPolicy`.
- **Methods:**
  - `extractFeatures(image)` -> CNN result tensor of shape `[B, 3, 24, 24]`.
  - `forward(image)` -> Tensor of logits `[B, 4]`.
  - `predict(image)` -> action key string (`"down"` | `"up"` | `"move"` | `"inject"`).
  - `reset()` -> no-op (kept for interface stability; the minimal policy is stateless).
  - `device` (property) -> current torch device.
  - `actionKeys` (property) -> the fixed action vocabulary tuple.

---

## Functions

*(None — all behaviour lives on the `Policy` class.)*

---

## Constants & Globals

### `C_ACTION_KEYS`
- **Type:** `tuple[str, ...]`
- **Value / Description:** `("down", "up", "move", "inject")` — fixed discrete action vocabulary.

### `C_NUM_ACTIONS`
- **Type:** `int`
- **Value / Description:** `4`

### `C_FEATURE_HEIGHT` / `C_FEATURE_WIDTH` / `C_FEATURE_CHANNELS`
- **Type:** `int`
- **Value / Description:** `24`, `24`, `3` — shape of the CNN result feature map.

### `C_FEATURE_DIM`
- **Type:** `int`
- **Value / Description:** `1728` (`24 * 24 * 3`) — flattened size of the CNN result before the classification head.

## Sample Usage

```python
from fluxCore.policy import Policy
import torch

policy = Policy(device="cpu")
image = torch.rand(3, 480, 270)          # any spatial size

features = policy.extractFeatures(image) # [1, 3, 24, 24]  <-- CNN result
actionKey = policy.predict(image)        # e.g. "down"
logits = policy.forward(image)           # [1, 4]
```
