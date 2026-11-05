## Overview & Design Context
`LocalDeviceStream` is the in-process stream layer between a `SCRCPYEmitter` and UI (or other) consumers. It owns decode, a `FrameRing`, and optional `StreamPresenter` presentation.

* **Design Decision / Deviation Notes:** Device switches are serialized via `switchDevice` + `asyncio.Lock`. Raw emitter `ON_FRAME` is not re-raised; only decoded `(FrameHeader, QImage)` is raised after ring publish/present. View presentation prefers `presentExternal`, falls back to `view.image`.

---

## Classes

### `LocalDeviceStream`
- **Purpose:** Single attach point for one emitter; decode once; present latest frame to an optional view.
- **Methods:**
  - `attachView(view)` / `detachView()` — bind capture surface.
  - `attachedEmitter(emitter)` / `detachedEmitter()` — subscribe lifecycle + codec init; frame path armed in `start`.
  - `start()` / `stop()` — arm `ON_FRAME` handler; forward stop to emitter.
  - `switchDevice(deviceManager, serial)` — serialized detach/stop → `ensureRunning` → attach/start.
  - `_onFrame(frame)` — decode, ring publish, present, raise decoded `ON_FRAME`.

## Sample Usage

```python
stream = LocalDeviceStream(ringSize=8)
stream.attachView(captureView)
await stream.switchDevice(deviceManager, serial)
# clear
await stream.switchDevice(deviceManager, None)
```
