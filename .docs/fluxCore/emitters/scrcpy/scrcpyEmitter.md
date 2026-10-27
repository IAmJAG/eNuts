## Overview & Design Context

`SCRCPYEmitter` streams device video/control via scrcpy. It is `AsyncService` + `SCRCPY`.

**Design:** Event payloads are never documented as the emitter instance. Metadata uses `SCRCPYEmitter.toScrcpy(...)` → `SCRCPY` (same object, no new instance). Errors use `ScrcpyErrorFootprint`.

---

## Classes

### `SCRCPYEmitter`

- **Purpose:** Async scrcpy session: initialize sockets/codec, emit frames and metadata.
- **Methods:**
  - `toScrcpy(emitter)` (classmethod) → `SCRCPY` — same object, not a new instance.
  - `initialize(GPUID, GPUReady)` → deploy server, sockets, metadata, codec; may raise after `ON_ERROR`.
  - `work` → frame loop; `ON_FRAME` / `ON_ERROR`.
  - `start` / `stop` — inherited `AsyncService` lifecycle events.

---

## Events

| Event | Payload |
|-------|---------|
| `ON_STARTING` / `ON_STARTED` / `ON_STOPPING` / `ON_STOPPED` | — |
| `ON_PAUSED` / `ON_RESUMED` | — |
| `ON_METADATA_UPDATE` | `SCRCPY` via `toScrcpy` |
| `ON_FRAME` | `iFrame` |
| `ON_ERROR` | `ScrcpyErrorFootprint` |

---

## Sample Usage

```python
from fluxCore.emitters.scrcpy import SCRCPYEmitter

emitter = SCRCPYEmitter(serial="...")

def onMeta(scrcpy):
    # scrcpy is typed as SCRCPY
    print(scrcpy.width, scrcpy.height, scrcpy.codecId)

def onError(err):
    print(err.phase, err.message, err.serial)

emitter.subscribe("ON_METADATA_UPDATE", onMeta)
emitter.subscribe("ON_ERROR", onError)
```
