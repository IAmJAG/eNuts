## Overview & Design Context

`SCRCPYEmitter` streams device video/control via scrcpy. It is `AsyncService` + `SCRCPY`.

**Metadata:** `SCRCPYEmitter.toScrcpy(emitter)` constructs a **base** `SCRCPY` and copies attributes. That is the only metadata snapshot type.

**Errors:** `ON_ERROR` raises with `(phase, message, serial)` strings — no dedicated error type.

---

## Classes

### `SCRCPYEmitter`

- **Methods:**
  - `toScrcpy(emitter)` (classmethod) → base `SCRCPY` with copied attributes.
  - `initialize` / `work` / `start` / `stop` as before.

---

## Events

| Event | Payload |
|-------|---------|
| Lifecycle (`ON_STARTED`, …) | — |
| `ON_METADATA_UPDATE` | base `SCRCPY` via `toScrcpy` |
| `ON_FRAME` | `iFrame` |
| `ON_ERROR` | `phase: str`, `message: str`, `serial: str` |

---

## Sample Usage

```python
def onMeta(scrcpy):
    print(scrcpy.width, scrcpy.height)

def onError(phase, message, serial):
    print(phase, message, serial)

emitter.subscribe("ON_METADATA_UPDATE", onMeta)
emitter.subscribe("ON_ERROR", onError)
```
