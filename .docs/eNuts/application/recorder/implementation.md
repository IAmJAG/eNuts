# Implementation Details

## 1. Architecture Overview
`KGRecorder` (QObject) holds `_state`, `_deviceId`, `_events`, binds to page `_captureImage` and `_deviceCombo`, and drives status/event list via signals. Shell wires CommandBar buttons and passes `deviceManager` via `setDeviceManager`.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/application/recorder/__kgRecorder.py` | `.docs/eNuts/application/recorder/kgRecorder.md` | Controller |
| `src/eNuts/types/interface/recorder/__iKGRecorder.py` | `.docs/eNuts/types/interface/recorder/iKGRecorder.md` | Contract |

## 3. Core Workflows
1. Shell: create `KGRecorder`, `setDeviceManager(mgr)`, bind page after WorkSpace is up.
2. Device events (`INITIALIZED` / `ADDED` / `REMOVED`) → `_sigDevicesChanged` → `_refreshDeviceCombo` (live combo).
3. Combo selection or `setDeviceId` → `_attachStream(serial)` (ensureRunning + ON_FRAME → CaptureImage via DeviceFrameBridge).
4. Start / Stop / Clear / Save / Open as before.

## 4. Deferred
- MP4 writer from SCRCPY frames (session-scoped continuous capture).
- Event file format and on-disk naming.
- Coordinate normalization vs stream resolution.
