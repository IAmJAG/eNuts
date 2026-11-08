## Overview & Design Context
`KGRecorder` page owns the device combo, `GLCanvas` stream surface, and recording UI state. Live video is driven by `LocalDeviceStream` / Presenter path. Session capture is delegated to `KGRecorderService`. Input from `GLCanvas` is injected to the selected device; successful injects are logged via the service while Recording.

* **Design Decision / Deviation Notes:** Device changes call `LocalDeviceStream.switchDevice` via `createTask`. Persistence key remains `RECORDER_DEVICE_ID`. Continuous recording only (Idle | Recording). Pointer inject uses `GLCanvas.mapToContent` then scales content→device resolution. Session artefacts land under `recordings/{sessionId}/`. Command bar Session group drives Record / Stop / Clear / Save. `CaptureGLImage` removed — use `jAGQt.widgets.Canvas.GLCanvas`.

---

## Classes

### `eKGRecorderState`
- **Purpose:** Idle | Recording.

### `KGRecorder`
- **Purpose:** Page UI + device list; recording I/O via `KGRecorderService`.
- **Methods:**
  - `_setDevice(deviceId)` — persist + `switchDevice` (blocked while Recording).
  - `_refreshDeviceCombo` — rebuild combo from `deviceManager`, then `_setDevice`.
  - `_wInitializeUI` — `GLCanvas` + utils strip; `stream.attachView` (until Presenter-owned view attach).
  - `_wireCaptureSignals` — connect key/mouse signals to inject handlers.
  - `_widgetToDevice(event)` — widget → `mapToContent` → device pixels; `None` if outside fit.
  - `start()` / `stop()` / `clear()` / `save(name)` — session control via service.

## Sample Usage

```python
from jAGQt.widgets.Canvas import GLCanvas

# Page constructs GLCanvas as _streamView; wires key/mouse signals for inject.
```
