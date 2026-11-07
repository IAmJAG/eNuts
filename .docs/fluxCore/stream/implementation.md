# Implementation Details

## 1. Architecture Overview

```text
DeviceManager.ensureRunning(serial)
  → SCRCPYEmitter
  → LocalDeviceStream (decode, FrameRing, StreamPresenter)
  → CaptureGLImage (presentExternal or image=)

KGRecorderService (parallel path)
  → emitter ON_FRAME → video.h264 (no ring skip)
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/stream/__deviceStream.py` | `.docs/fluxCore/stream/deviceStream.md` | Stream + switch |
| `src/fluxCore/stream/__frameRing.py` | `.docs/fluxCore/stream/frameSlot.md` (design) | Latest-frame buffer |
| `src/fluxCore/stream/__streamPresenter.py` | — | GUI present helper |
| `src/eNuts/UI/pages/__kgRecorder.py` | `.docs/eNuts/UI/pages/kgRecorderPage.md` | Page uses stream for preview |
| `src/eNuts/services/recorder/__kgRecorderService.py` | `.docs/eNuts/services/recorder/kgRecorderService.md` | Capture every frame |

## 3. Core Workflows
1. Page `_setDevice` → `createTask(stream.switchDevice, deviceManager, serial)`.
2. `switchDevice` under lock: detach/stop → `ensureRunning` → `attachedEmitter` → `start`.
3. Emitter `ON_FRAME` → stream `_onFrame` → ring → present → raise decoded frame event.
4. Recording does **not** read the ring; service binds the same emitter and writes every payload.
