## Overview & Design Context

`DCPolicy` is the L1 history buffer. It transforms the current image, keeps circular histories, pads them to `stackSize`, and calls `DCPolicyCore.forward`.

* **Design Decision / Deviation Notes:** History length comes from `options.stackSize`, not a constructor argument. See `requirement.md` FR-16.

---

## Classes

### `DCPolicy`
- **Purpose:** L1 wrapper over `DCPolicyCore`. Owns the image transform and four circular buffers.
- **Methods:**
  - `__init__(module=None, device="cuda", *args, **kwargs)` → builds the core, the transform, and the deques.
  - `forward(activeIntent, previousIntent, image, previousAction, previousParameters)` → appends, stacks, returns the core dict.
  - `_stack(buf)` → stacks the deque and zero-pads the front to `maxlen`.

---

## Functions

None.

---

## Constants & Globals

None. Length and image size come from `PolicyOptions`.

## Sample Usage

```python
from fluxCore.policy import DCPolicy

policy = DCPolicy(stackSize=8, frameSize=224)
out = policy(activeIntent, previousIntent, image, previousAction, previousParameters)
# out["ACTION"], out["PARAMETERKIND"], out["SPATIAL"]
```
