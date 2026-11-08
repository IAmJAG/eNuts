## Overview & Design Context
`LocalDeviceStream` is the in-process stream layer between a `SCRCPYEmitter` and registered `iFrameConsumer`s. It owns the `FrameRing`, codec sync, and consumer lifecycle. Decode is scheduled inside the ring; the stream does not present frames.

* **Design Decision / Deviation Notes:** `_onFrame` only calls `ring.publish(packet, codec)` then optional stream-level `ON_FRAME` fan-out with the **packet** (not a Tensor/QImage). A default `Presenter` is registered at construction; `attachView` / `detachView` forward to that presenter. Additional consumers use `registerConsumer` / `unregisterConsumer`.

---

## Classes

### `LocalDeviceStream`
- **Purpose:** Single attach point for one emitter; publish packets to the ring; start/stop frame consumers.
- **Properties:** `ring`, `presenter`
- **Methods:**
  - `registerConsumer` / `unregisterConsumer` — attach/detach ring; start if stream running.
  - `attachView` / `detachView` — convenience on the default `Presenter`.
  - `attachedEmitter` / `detachedEmitter` — lifecycle + codec wiring.
  - `start` / `stop` — arm `ON_FRAME`; start/stop all consumers.
  - `switchDevice(deviceManager, serial)` — coalesced detach/stop → `ensureRunning` → attach/start.
  - `_onFrame(packet)` — `ring.publish(packet, codec)` only.

## Sample Usage

```python
stream = LocalDeviceStream(ringSize=8)
stream.attachView(glCanvas)   # → stream.presenter.attachView
await stream.switchDevice(deviceManager, serial)
# clear
await stream.switchDevice(deviceManager, None)
```
