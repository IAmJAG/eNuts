## Overview & Design Context

`SCRCPYEmitter` streams Android video/control via scrcpy. It combines `AsyncService` and `SCRCPY`.

* **Design:** Event payloads never pass the emitter instance. Metadata uses a base `SCRCPY` from `toScrcpy`. Errors use `SCRCPYError`. All emitter-raised events use `asyncRaiseEvent`.
* **Metadata header:** After video + control sockets connect, `_updateMetadata` reads the 64B device name + 4B codec + 4B width + 4B height from the **video** socket. Each field is guarded by `wait_for` (`C_METADATA_TIMEOUT_S`, default 5s). A hang or timeout raises `ConnectionError` through `initialize.metadata` so `DeviceManager.ensureRunning` fails visibly instead of blocking forever.

---

## Classes

### `SCRCPYEmitter`

- **Purpose:** Async scrcpy session — deploy server, open sockets, emit frames and metadata.
- **Methods:**
  - `toScrcpy(emitter)` (classmethod) → base `SCRCPY` with copied `id`/`name`/`codecId`/`width`/`height`.
  - `initialize(GPUID, GPUReady)` → deploy, sockets, metadata (timed), codec; may `ON_ERROR` then re-raise.
  - `_updateMetadata(sckt, timeout)` → timed header read; emits `metadata begin` then `metadata id=…` on success.
  - `work` → frame loop until stopped (`frame id=… n=…` traces for n≤3 and every 30th).
  - `ControlSocket` (property) → control channel or `None`.
  - Inherited: `start` / `stop` / `pause` / `resume` (`AsyncService`).

---

## Events

| Event | Payload |
|-------|---------|
| `ON_STARTING` / `ON_STARTED` / `ON_STOPPING` / `ON_STOPPED` | — |
| `ON_PAUSED` / `ON_RESUMED` | — |
| `ON_METADATA_UPDATE` | base `SCRCPY` |
| `ON_FRAME` | `iFrame` |
| `ON_ERROR` | `SCRCPYError` / `RuntimeError` |
| `ON_INITIALIZED` | codec context (local) |

---

## Sample Usage

```python
from fluxCore.emitters.scrcpy import SCRCPYEmitter, SCRCPYError
from fluxCore.devices import SCRCPY

emitter = SCRCPYEmitter(serial="...")

async def onMeta(scrcpy: SCRCPY) -> None:
    assert type(scrcpy) is SCRCPY
    print(scrcpy.width, scrcpy.height, scrcpy.codecId)

async def onError(err: SCRCPYError) -> None:
    print(err.phase, err.message, err.serial)

emitter.subscribe("ON_METADATA_UPDATE", onMeta)
emitter.subscribe("ON_ERROR", onError)
```
