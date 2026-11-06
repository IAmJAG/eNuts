# Implementation Details

## 1. Architecture Overview
`Shell` → `deviceManager` (discovery + emitters) → pages consume via `shell.deviceManager` / `shell.settings`.

Recording controller lives inside `UI/pages/__kgRecorder.py`; Shell does not create or bind it.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/application/__shell.py` | `.docs/eNuts/application/shell/shell.md` | Shell wiring |
| `src/eNuts/application/device/__deviceManager.py` | `.docs/eNuts/application/device/deviceManager.md` | Device registry |
| `src/eNuts/UI/pages/__kgRecorder.py` | `.docs/eNuts/UI/pages/kgRecorderPage.md` | Recorder page + controller |

## 3. Core Workflows & Data Flow
1. `_wInitializeUI` → `deviceManager(shutdownEvent)` + `runDiscovery()`.
2. `WorkSpace` central widget → pages registered (including KG Recorder page).
3. KG Recorder page uses `shell.deviceManager` and `shell.settings` directly.
4. `closeEvent` → `stopAll` → `_shutdownEvent.set()`.
