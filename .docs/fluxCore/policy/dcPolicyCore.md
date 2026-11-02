## Overview & Design Context

`DCPolicyCore` is the L2 model. It runs a visual backbone, merges history, blankets the active intent, and emits three heads.

* **Design Decision / Deviation Notes:** Stateless across calls. No `stateReset`. `forward` is deterministic. Inference-time noise is not an option here; it belongs to the inference implementation. See `implementation.md` section 4.

---

## Classes

### `DCPolicyCore`
- **Purpose:** `nn.Module` implementing `iPolicy`. Default backbone is MobileNet V3 Small.
- **Methods:**
  - `__init__(module=None, device="cuda", *args, **kwargs)` → builds options, backbone, merges, and heads.
  - `forward(intent, intentSpace, visualSpace, actionSpace, parameterSpace)` → `{"ACTION", "PARAMETERKIND", "SPATIAL"}`. No noise.
  - `save(path)` → writes `VERSION`, `MODELSTATE`, `OPTIONS`.
  - `load(path, module=None, device="cuda")` (classmethod) → rebuilds and `load_state_dict(strict=True)`.
  - `options` / `device` → properties.

---

## Functions

None in this file. Backbone construction is in `utilities.md`.

---

## Constants & Globals

### `VERSION`
- **Type:** `str`
- **Value / Description:** `"0.0.1"`. `load` rejects any other value.

## Sample Usage

```python
from fluxCore.policy import DCPolicyCore

core = DCPolicyCore()
out = core(intent, intentSpace, visualSpace, actionSpace, parameterSpace)
core.save("policy.pt")
loaded = DCPolicyCore.load("policy.pt")
```
