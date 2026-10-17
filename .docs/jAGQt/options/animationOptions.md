## Overview & Design Context
Serializable settings applied to an animation at construction/apply time, then dropped. Animation owns runtime config afterward.

---

## Classes

### `AnimationOptions`
- **Purpose:** Duration (and future shared animation scalars).
- **Properties:**
  - `durationMs` — non-negative int.

---

## Constants & Globals

### `C_DEFAULT_DURATION_MS`
- **Type:** `int`
- **Value / Description:** `280`

## Sample Usage

```python
from jAGQt.options import AnimationOptions

animOpts = AnimationOptions(name="RubberBand", durationMs=280)
```
