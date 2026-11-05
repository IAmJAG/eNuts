## Overview & Design Context
`KGRecorder` page is a view with device combo and `CaptureGLImage` stream surface. Live video is driven exclusively by `LocalDeviceStream` (decode, ring, present). The page does not subscribe to emitters or decode frames.

* **Design Decision / Deviation Notes:** Device changes call `LocalDeviceStream.switchDevice` via `createTask`. Persistence key remains `RECORDER_DEVICE_ID`. Application-level controller (`application/recorder/KGRecorder`) is a separate component and is not required for this stream path.

---

## Classes

### `KGRecorder`
- **Purpose:** Page UI + device list; stream lifecycle delegated to `LocalDeviceStream`.
- **Methods:**
  - `_setDevice(deviceId)` — persist + `switchDevice`.
  - `_refreshDeviceCombo` — rebuild combo from `deviceManager`, then `_setDevice`.
  - `_wInitializeUI` — `CaptureGLImage` + utils strip; `stream.attachView`.

## Sample Usage

```python
# Page is registered by navigation/shell; stream starts when a device is selected.
```
