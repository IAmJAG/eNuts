# Implementation Details

## 1. Architecture Overview
- **Page / controller:** `KGRecorder` in `src/eNuts/UI/pages/__kgRecorder.py` owns Idle|Recording UI state, device combo, inject, and `LocalDeviceStream` preview.
- **Capture service:** `KGRecorderService` (`src/eNuts/services/recorder/`) writes every emitter `ON_FRAME` + key/pointer events.
- **Wiring:** Shell only exposes `deviceManager` + `settings`. Page binds service, stream, and CaptureGLImage itself.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/UI/pages/__kgRecorder.py` | `.docs/eNuts/UI/pages/kgRecorderPage.md` | Page + session UI controller |
| `src/eNuts/UI/pages/__recorderState.py` | (enum) | `eKGRecorderState` |
| `src/eNuts/UI/widgets/__captureGLImage.py` | `.docs/eNuts/UI/widgets/captureGLImage.md` | GL view + input signals |
| `src/eNuts/services/recorder/__kgRecorderService.py` | `.docs/eNuts/services/recorder/kgRecorderService.md` | Session capture I/O |
| `src/eNuts/types/interface/services/recorder/__iKGRecorderService.py` | (interface) | Protocol contract |
| `src/eNuts/services/device/__deviceManager.py` | `.docs/eNuts/services/device/deviceManager.md` | Device registry |

## 3. Core Workflows & Data Flow
1. Page constructs `LocalDeviceStream` + `KGRecorderService`.
2. Device combo refreshed from `deviceManager` events; selection → `switchDevice`.
3. `start()` → `bind(emitter, serial=…, width=…, height=…, codec=…)` + `start(sessionDir)` under `recordings/`.
4. CaptureGLImage key/mouse → inject + `logKey` / `logPointer` while Recording.
5. `stop()` → service finalizes `video.h264` + `session.json`; UI returns to Idle.
6. Save/Open remain deferred (log paths from last result).

## 4. Deferred
- Precise image-fit transform / coordinate polish.
- Save/Open paired artefacts UX and naming convention.
- MP4 remux (v1 is elementary h264 + JSON events).
