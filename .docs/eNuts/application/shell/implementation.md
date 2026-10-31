# Implementation Details

## 1. Architecture Overview
`Shell` → `deviceManager` (discovery + emitters) → `KGRecorder.setDeviceManager` → page bind (`PAGE_KG_RECORDER`).

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/application/__shell.py` | `.docs/eNuts/application/shell/shell.md` | Shell wiring |
| `src/eNuts/application/device/__deviceManager.py` | `.docs/eNuts/application/device/deviceManager.md` | Device registry |
| `src/eNuts/application/recorder/__kgRecorder.py` | `.docs/eNuts/application/recorder/kgRecorder.md` | Recorder controller |

## 3. Core Workflows & Data Flow
1. `_wInitializeUI` → `_ensureManagers` → `deviceManager(shutdownEvent)` + `runDiscovery()`.
2. `KGRecorder(parent=self)` → `setDeviceManager(mgr)` (subscribe to DEVICE_* events).
3. `WorkSpace` central widget → pages registered → `_bindKgRecorderPage` → `bindPage`.
4. `closeEvent` → `stopAll` → `_shutdownEvent.set()`.
