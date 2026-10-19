## Overview & Design Context

Minimal policy implementation located at `src/fluxCore/policy/__policy.py`.

Accepts a single image and returns one discrete action key from the fixed vocabulary: `down`, `up`, `move`, `inject`.

* **Design Decision / Deviation Notes:** Starts with a tiny CNN backbone sized for the 24×24 internal resolution. Advanced features (intent, history, continuous arguments, temporal stack) are intentionally deferred. See the project-level requirements at `.docs/policy/requirement.md`.

---

## Classes

### `Policy`
- **Purpose:** Minimal image-to-action model. Implements `iPolicy`.
- **Methods:**
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

### `C_INPUT_HEIGHT` / `C_INPUT_WIDTH` / `C_INPUT_CHANNELS`
- **Type:** `int`
- **Value / Description:** `24`, `24`, `3` — internal tensor shape after pre-processing.

## Sample Usage

```python
from fluxCore.policy import Policy
import torch

policy = Policy(device="cpu")
# image can be [C,H,W] or [B,C,H,W]; any spatial size is resized to 24x24
image = torch.rand(3, 128, 128)
actionKey = policy.predict(image)   # e.g. "down"
logits = policy.forward(image)      # shape [1, 4]
```
