## Overview & Design Context

`SCRCPYEmitter` is `AsyncService` + `SCRCPY`.

- **Metadata:** `toScrcpy` → base `SCRCPY` (construct + copy attrs).
- **Errors:** `ON_ERROR` → `SCRCPYError` (`__footprint.py`).

---

## Events

| Event | Payload |
|-------|---------|
| Lifecycle | — |
| `ON_METADATA_UPDATE` | base `SCRCPY` |
| `ON_FRAME` | `iFrame` |
| `ON_ERROR` | `SCRCPYError` |
| `ON_INITIALIZED` | codec context (local) |

---

## Sample

```python
from fluxCore.emitters.scrcpy import SCRCPYEmitter, SCRCPYError

def onError(err: SCRCPYError) -> None:
    print(err.phase, err.message, err.serial)
```
