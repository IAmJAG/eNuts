# Implementation Details

## 1. Architecture Overview
`DeviceManager(AsyncSubscription)` + `SCRCPYDevices()` discovery → `_devices` map → events → `KGRecorder` combo refresh / stream attach.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/services/device/__deviceManager.py` | `.docs/eNuts/services/device/deviceManager.md` | Registry |
| `src/eNuts/services/device/__init__.py` | (exports) | Public surface |
| `src/eNuts/types/interface/services/device/__deviceManager.py` | (interface) | `iDeviceManager` protocol |

## 3. Core Workflows & Data Flow
1. Shell constructs `DeviceManager(shutdownEvent)` and calls `runDiscovery`.
2. Initial scan suppresses events, adds devices, then raises `DEVICE_INITIALIZED_EVENT`.
3. Poll loop diffs ids → `add` / `remove`.
4. `KGRecorder` subscribes to the three device events via `deviceManager`.
5. `ensureRunning` initializes SCRCPYEmitter (`GPUReady=False`) once, then starts.
