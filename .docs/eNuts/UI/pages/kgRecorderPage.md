## Overview & Design Context
`KGRecorder` page owns the device combo, `CaptureGLImage` stream surface, and the recording controller. Live video is driven exclusively by `LocalDeviceStream` (decode, ring, present). The page does not subscribe to emitters or decode frames itself.

* **Design Decision / Deviation Notes:** Device changes call `LocalDeviceStream.switchDevice` via `createTask`. Persistence key remains `RECORDER_DEVICE_ID`. Application-level controller has been removed; recording logic lives inside this page.

---

## Classes

### `KGRecorder`
- **Purpose:** Page UI + device list + recording controller; stream lifecycle delegated to `LocalDeviceStream`.
- **Methods:**
  - `_setDevice(deviceId)` — persist + `switchDevice`.
  - `_refreshDeviceCombo` — rebuild combo from `deviceManager`, then `_setDevice`.
  - `_wInitializeUI` — `CaptureGLImage` + utils strip; `stream.attachView`.
  - (recording) start / stop / clear / save / open — to be reconstructed on the page.

## Sample Usage

```python
# Page is registered by navigation; stream starts when a device is selected.
# Recording session is owned by the page instance.
```
