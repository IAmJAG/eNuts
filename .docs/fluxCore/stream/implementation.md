# Implementation Details

## 1. Architecture Overview

```text
DeviceManager.ensureRunning(serial)
  → SCRCPYEmitter
  → LocalDeviceStream (owns FrameRing; non-frame events/errors)
  → FrameRing.publish(packet) → async decode → FILLED slots
  → Presenter latest() / Recorder next()+release()
  → CaptureGLImage (present path, later)
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/__deviceStream.py` | `.docs/fluxCore/stream/deviceStream.md` | Stream + switch |
| `src/fluxCore/stream/frameRing/__frameRing.py` | `.docs/fluxCore/stream/frameRing/frameRing.md` | Process-then-cache ring |
| `src/fluxCore/stream/frameRing/slot/` | `.docs/fluxCore/stream/frameRing/slot/` | Slot + flags |
| `src/fluxCore/stream/__streamPresenter.py` | — | GUI present helper |
| `src/eNuts/UI/pages/__kgRecorder.py` | `.docs/eNuts/UI/pages/kgRecorderPage.md` | Page preview + inject |

## 3. Core Workflows & Data Flow
1. Page `_setDevice` → `createTask(stream.switchDevice, deviceManager, serial)`.
2. `switchDevice` under lock: detach → `ensureRunning` → attach → start.
3. Emitter `ON_FRAME` → `FrameRing.publish` (non-blocking decode task).
4. UI: `latest()`; capture: `next()` + `release(slot)`.

**Note:** Parent `requirement.md` FR-3/FR-4 still describe the older stream-owned QImage path; ring package is the active design for process-then-cache. Wire-up of `LocalDeviceStream` to the new `publish(packet, decoder)` API may still be pending on this branch.
