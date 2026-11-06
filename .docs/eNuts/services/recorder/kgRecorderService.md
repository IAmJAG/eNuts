## Overview & Design Context
`KGRecorderService` records one device session: every encoded SCRCPY frame packet to `video.h264` and key/pointer events into a single JSON array in `session.json`. Capture is driven by the emitter `ON_FRAME` path (not `LocalDeviceStream` / `FrameRing`), so frames are never skipped for display-ring reasons.

* **Design Decision / Deviation Notes:** Video container is the raw elementary stream already carried on `iFrame.payload` (PyAV is used elsewhere for decode only; no new mux dependency). No pause API. Page `KGRecorder` remains UI/inject; this service owns durable I/O.

---

## Classes

### `KGRecorderService`
- **Purpose:** AsyncService that binds an `iEmitter`, writes every `ON_FRAME` payload, and accumulates input events until `stop()`.
- **Methods:**
  - `bind(emitter, *, serial, width, height, codec="h264")` — attach emitter metadata; forbidden while recording.
  - `start(sessionDir)` — create dir, open `video.h264`, subscribe `ON_FRAME`, mark recording.
  - `stop()` → manifest dict — unsubscribe, close video, write `session.json`, return paths/counts.
  - `logKey(action, key)` / `logPointer(action, x, y)` — append event with relative `t` while recording.
  - `clearEvents()` — empty event list; resets relative clock if still recording.
- **Events:** `ON_SESSION_STARTED`, `ON_SESSION_STOPPED`, `ON_ERROR`.

## Constants & Globals

### `C_ON_SESSION_STARTED` / `C_ON_SESSION_STOPPED` / `C_ON_ERROR`
- **Type:** `str`
- **Value / Description:** Service subscription event names.

### `C_VIDEO_NAME` / `C_MANIFEST_NAME`
- **Type:** `str`
- **Value / Description:** `video.h264`, `session.json` basenames inside the session directory.

### `C_MANIFEST_VERSION`
- **Type:** `int`
- **Value / Description:** Manifest schema version (`1`).

## Sample Usage

```python
from eNuts.services.recorder import KGRecorderService, C_ON_SESSION_STOPPED

svc = KGRecorderService()
svc.bind(emitter, serial=serial, width=w, height=h, codec="h264")
svc.subscribe(C_ON_SESSION_STOPPED, onStopped)
svc.start("/path/to/recordings/session-001")
# ... logKey / logPointer while recording ...
result = svc.stop()
```
