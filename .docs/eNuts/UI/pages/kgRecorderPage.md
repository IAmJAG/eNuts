## Overview & Design Context
`KGRecorder` page owns the device combo, `CaptureGLImage` stream surface, and the recording controller. Live video is driven exclusively by `LocalDeviceStream` (decode, ring, present). Input from `CaptureGLImage` is injected to the selected device; successful injects are logged while Recording.

* **Design Decision / Deviation Notes:** Device changes call `LocalDeviceStream.switchDevice` via `createTask`. Persistence key remains `RECORDER_DEVICE_ID`. Controller lives inside the page (no Shell wiring). Continuous recording only (Idle | Recording). Widget→device coordinate fit transform is a simple scale for now; precise image-fit mapping is deferred. Save/Open (paired MP4 + events) deferred.

---

## Classes

### `eKGRecorderState`
- **Purpose:** Idle | Recording.

### `KGRecorder`
- **Purpose:** Page UI + device list + recording controller; stream lifecycle via `LocalDeviceStream`.
- **Methods:**
  - `_setDevice(deviceId)` — persist + `switchDevice` (blocked while Recording).
  - `_refreshDeviceCombo` — rebuild combo from `deviceManager`, then `_setDevice`.
  - `_wInitializeUI` — `CaptureGLImage` + utils strip; `stream.attachView`.
  - `_wireCaptureSignals` — connect key/mouse signals to inject handlers.
  - `start()` / `stop()` / `clear()` — session transport.
  - `save(name)` / `open(name)` — persistence stubs (deferred).
  - `_onKeyPressed` / `_onKeyReleased` / `_onMouse*` — inject + optional log.

## Sample Usage

```python
# Page is registered by navigation; stream starts when a device is selected.
# page.start() / page.stop() control the recording session.
```
