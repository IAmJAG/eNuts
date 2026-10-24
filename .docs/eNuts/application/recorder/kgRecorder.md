## Overview & Design Context
`KGRecorder` is the Key & Gesture Recorder controller. It is a component of ENUTSWindow, created and wired from Shell. It owns session state, event collection, and (later) paired MP4 + event-file persistence.

* **Design Decision / Deviation Notes:** Continuous recording only (no pause). Save/Open file naming is intent-dependent and deferred. Coordinates are currently widget-space; normalization to stream resolution is deferred.

---

## Classes

### `KGRecorder`
- **Purpose:** External controller for the kg-recorder page.
- **Methods:**
  - `start()` / `stop()` / `clear()` — session transport.
  - `save(name)` / `open(name)` — persistence stubs (paired MP4 + events).
  - `setDeviceId(deviceId)` — bind target device (blocked while recording).
  - `bindPage(page)` / `unbindPage()` — connect/disconnect CaptureImage signals and view updates.
- **Signals:** `stateChanged`, `eventsChanged`, `statusTextChanged`.

## Sample Usage

```python
from eNuts.application.recorder import KGRecorder

recorder = KGRecorder(parent=window)
recorder.bindPage(page)
recorder.setDeviceId(serial)
recorder.start()
```
