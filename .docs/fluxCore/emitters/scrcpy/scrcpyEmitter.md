## Overview & Design Context

`SCRCPYEmitter` streams device video/control via scrcpy. It is `AsyncService` + `SCRCPY`.

**Metadata footprint:** `SCRCPYEmitter.toScrcpy(emitter)` constructs a **base** `SCRCPY` (not the emitter, not a subclass), copies `id`/`name`/`codecId`/`width`/`height`, and returns that instance. No separate footprint type.

---

## Classes

### `SCRCPYEmitter`

- **Purpose:** Async scrcpy session: initialize sockets/codec, emit frames and metadata.
- **Methods:**
  - `toScrcpy(emitter)` (classmethod) → **new** base `SCRCPY` with attributes copied from the emitter.
  - `initialize(GPUID, GPUReady)` → deploy, sockets, metadata, codec; may raise after `ON_ERROR`.
  - `work` → frame loop; `ON_FRAME` / `ON_ERROR`.
  - `start` / `stop` — inherited `AsyncService` lifecycle events.

---

## Events

| Event | Payload |
|-------|---------|
| `ON_STARTING` / `ON_STARTED` / `ON_STOPPING` / `ON_STOPPED` | — |
| `ON_PAUSED` / `ON_RESUMED` | — |
| `ON_METADATA_UPDATE` | base `SCRCPY` via `toScrcpy` |
| `ON_FRAME` | `iFrame` |
| `ON_ERROR` | `ScrcpyErrorFootprint` |

---

## Sample Usage

```python
from fluxCore.emitters.scrcpy import SCRCPYEmitter
from fluxCore.devices import SCRCPY

emitter = SCRCPYEmitter(serial="...")

def onMeta(scrcpy: SCRCPY) -> None:
    assert type(scrcpy) is SCRCPY  # not SCRCPYEmitter
    print(scrcpy.width, scrcpy.height, scrcpy.codecId)

def onError(err) -> None:
    print(err.phase, err.message, err.serial)

emitter.subscribe("ON_METADATA_UPDATE", onMeta)
emitter.subscribe("ON_ERROR", onError)
```
