## Overview & Design Context
`KGRecorder` page owns the device combo, `CaptureGLImage` stream surface, and recording UI state. Live video is driven by `LocalDeviceStream` (decode, ring, present). Session capture is delegated to `KGRecorderService` (every emitter `ON_FRAME` → `video.h264`, key/pointer events → `session.json`). Input from `CaptureGLImage` is injected to the selected device; successful injects are logged via the service while Recording.

* **Design Decision / Deviation Notes:** Device changes call `LocalDeviceStream.switchDevice` via `createTask`. Persistence key remains `RECORDER_DEVICE_ID`. Continuous recording only (Idle | Recording). Pointer inject uses `GLImage.mapToContent` then scales content→device resolution. Session artefacts land under `recordings/{sessionId}/`.

---

## Classes

### `eKGRecorderState`
- **Purpose:** Idle | Recording.

### `KGRecorder`
- **Purpose:** Page UI + device list; recording I/O via `KGRecorderService`.
- **Methods:**
  - `_setDevice(deviceId)` — persist + `switchDevice` (blocked while Recording).
  - `_refreshDeviceCombo` — rebuild combo from `deviceManager`, then `_setDevice`.
  - `_wInitializeUI` — `CaptureGLImage` + utils strip; `stream.attachView`.
  - `_wireCaptureSignals` — connect key/mouse signals to inject handlers.
  - `_widgetToDevice(event)` — widget → `mapToContent` → device pixels; `None` if outside fit.
  - `start()` — bind emitter to `KGRecorderService`, start session under `recordings/`.
  - `stop()` — finalize service session; restore device combo.
  - `clear()` — `recorder.clearEvents()`.
  - `save(name)` — stop if still recording; log paths from last result.
  - `_logEvent` — routes to `logKey` / `logPointer` on the service.

## Sample Usage

```python
from eNuts.services.recorder import KGRecorderService

# Page is registered by navigation; stream starts when a device is selected.
# page.start() / page.stop() control the recording session via KGRecorderService.
```
