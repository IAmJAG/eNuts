# Implementation Details

## 1. Architecture Overview
`deviceManager(AsyncSubscription)` + `SCRCPYDevices()` discovery → `_devices` map → events → `KGRecorder` combo refresh / stream attach.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/application/device/__deviceManager.py` | `.docs/eNuts/application/device/deviceManager.md` | Registry |
| `src/eNuts/application/device/__init__.py` | (exports) | Public surface |

## 3. Core Workflows & Data Flow
1. Shell constructs `deviceManager(shutdownEvent)` and calls `runDiscovery`.
2. Initial scan suppresses events, adds devices, then raises `DEVICE_INITIALIZED_EVENT`.
3. Poll loop diffs ids → `addDevice` / `removeDevice`.
4. `KGRecorder.setDeviceManager` subscribes to the three device events.
5. `ensureRunning` initializes SCRCPYEmitter (GPUReady=False) once, then starts.
