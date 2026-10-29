## Overview & Design Context

Module `__footprint.py` holds serializable payloads used at event / future IPC boundaries that are **not** a base `SCRCPY`.

Metadata uses `SCRCPYEmitter.toScrcpy` → base `SCRCPY` (not defined in this file).

---

## Classes

### `SCRCPYError`

- **Purpose:** Serializable error detail for `ON_ERROR` (and later `ScrcpyErrorMessage`).
- **Properties:**
  - `phase` — e.g. `initialize.deploy`, `initialize.socket`, `initialize.metadata`, `initialize.codec`, `work`
  - `message` — human-readable summary
  - `serial` — device id when known

---

## Sample Usage

```python
from fluxCore.emitters.scrcpy import SCRCPYError

err = SCRCPYError(phase="initialize.deploy", message="Failed to deploy", serial="ABC")
print(err.phase, err.message, err.serial)
```
