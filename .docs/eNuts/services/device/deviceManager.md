## Overview & Design Context
`DeviceManager` discovers ADB/SCRCPY devices, stores `iDevice` instances (typically `SCRCPYEmitter`), and raises add/remove/initialized events for UI and recorder consumers.

* **Design Decision / Deviation Notes:** Lives under `eNuts.services.device` (not `application`). Shell constructs one instance bound to the window shutdown event. Class name is PascalCase (`DeviceManager`) per public-class convention. Stream readiness is tracked separately so `ensureRunning` can initialize + start emitters on demand.

---

## Classes

### `DeviceManager`
- **Purpose:** Async device registry with polling discovery and SCRCPY emitter lifecycle helpers.
- **Methods:**
  - `runDiscovery()` — schedule `_discovery` task.
  - `add(device)` / `remove(device|str)` — registry mutations + events.
  - `get(deviceId)` / `ensureRunning(deviceId)` — SCRCPY access and start.
  - `start(device)` / `stop(device)` / `stopAll()` / `stopExcept(keepDeviceId)` — emitter lifecycle helpers.
- **Events:** `DEVICE_ADDED_EVENT`, `DEVICE_REMOVED_EVENT`, `DEVICE_INITIALIZED_EVENT`.

## Constants & Globals

### `DEVICE_ADDED_EVENT` / `DEVICE_REMOVED_EVENT` / `DEVICE_INITIALIZED_EVENT`
- **Type:** `str`
- **Value / Description:** Event names raised on the AsyncSubscription surface.

### `POLL_INTERVAL`
- **Type:** `float`
- **Value / Description:** Seconds between discovery polls (2.0).

## Sample Usage

```python
from eNuts.services.device import (
    DeviceManager,
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
)

mgr = DeviceManager(shutdownEvent)
mgr.subscribe(DEVICE_ADDED_EVENT, onAdded)
mgr.runDiscovery()
emitter = await mgr.ensureRunning(serial)
```
