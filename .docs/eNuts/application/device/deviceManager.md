## Overview & Design Context
`deviceManager` discovers ADB/SCRCPY devices, stores `iDevice` instances (typically `SCRCPYEmitter`), and raises add/remove/initialized events for UI and recorder consumers.

* **Design Decision / Deviation Notes:** Class name is camelCase (`deviceManager`) per internal-class convention. Stream readiness is tracked separately so `ensureRunning` can initialize + start emitters on demand.

---

## Classes

### `deviceManager`
- **Purpose:** Async device registry with polling discovery and SCRCPY emitter lifecycle helpers.
- **Methods:**
  - `runDiscovery()` — schedule `_discovery` task.
  - `addDevice(device)` / `removeDevice(device|str)` — registry mutations + events.
  - `getEmitter(deviceId)` / `ensureRunning(deviceId)` — SCRCPY access and start.
  - `stopAll()` / `stopExcept(keepDeviceId)` — emitter shutdown helpers.
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
from eNuts.application.device import deviceManager, DEVICE_ADDED_EVENT

mgr = deviceManager(shutdownEvent)
mgr.subscribe(DEVICE_ADDED_EVENT, onAdded)
mgr.runDiscovery()
emitter = await mgr.ensureRunning(serial)
```
