# Implementation Details

## 1. Architecture Overview
`KGRecorderService(AsyncService)` binds an `iEmitter`, subscribes to `ON_FRAME`, appends `frame.payload` to `video.h264`, and collects input events until `stop()` writes `session.json`.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/services/recorder/__kgRecorderService.py` | `.docs/eNuts/services/recorder/kgRecorderService.md` | Session capture service |
| `src/eNuts/services/recorder/__init__.py` | (exports) | Public surface |
| `src/eNuts/types/interface/services/recorder/__iKGRecorderService.py` | (interface) | Protocol contract |

## 3. Core Workflows & Data Flow
1. Page/controller calls `bind(emitter, serial=..., width=..., height=...)`.
2. `start(sessionDir)` creates directory, opens `video.h264`, clears events, subscribes `ON_FRAME`.
3. Each `ON_FRAME` writes payload bytes; `logKey` / `logPointer` append `{t, kind, ...}`.
4. `stop()` unsubscribes, closes video, writes manifest JSON array under `events`, raises `ON_SESSION_STOPPED`.
5. Live preview continues via `LocalDeviceStream` independently (ring may drop; recorder does not).
