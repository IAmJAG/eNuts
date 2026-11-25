## Overview & Design Context
Out-of-process device discovery worker. Polls ADB, emits Handshake, Heartbeat, DeviceDiscoveryStarted/Ended, InitializeDeviceList, DeviceAdded, DeviceRemoved messages to the parent ProcessHost.

* **Design Decision / Deviation Notes:** Replaces the old in-process DeviceManager. Runs as a module-level coroutine (`deviceWatcher`) under ProcessHost. Uses fixed-margin heartbeat (BEAT - 0.2s). POLL_INTERVAL = 0.1s.

---

## Functions

### `deviceWatcher(shutdownEvent, inQueue, outQueue)`
- **Arguments:** shutdownEvent (syncEvent), inQueue (Queue), outQueue (Queue)
- **Returns:** None (async)
- **Behavior:** Starts watcher task, sends Handshake, waits. On exit sends Terminated. Entry point for the client process.

### `_messageHandler(msg, shutdownEvent, inQueue, outQueue)`
- **Behavior:** On Handshake, starts `_discovery` and `_beat` tasks.

### `_beat(shutdownEvent, queue)`
- **Behavior:** Sends Heartbeat(BEAT=2.0) every INTERVAL = max(0.05, BEAT - 0.2) until shutdown.

### `_discovery(shutdownEvent, queue)`
- **Behavior:** Sends DeviceDiscoveryStarted, queries ADBDevices, sends InitializeDeviceList, then polls for added/removed devices (DeviceAdded/DeviceRemoved), finally DeviceDiscoveryEnded.

## Constants & Globals

### `POLL_INTERVAL`
- **Type:** `float`
- **Value / Description:** 0.1 seconds between discovery polls.

## Sample Usage

```python
# Started by ProcessHost with worker=deviceWatcher
# Parent receives Handshake, then discovery messages and periodic Heartbeats.
```
