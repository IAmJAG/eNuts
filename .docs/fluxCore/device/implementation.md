# Implementation Details

## 1. Architecture Overview
Thin inheritance: Device (Serializable + iDevice) → SCRCPYDevice (ADB queries). Used by out-of-process deviceManager client to report discovered devices.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/fluxCore/device/__device.py` | `.docs/fluxCore/device/device.md` | Base Device |
| `src/fluxCore/device/__SCRCPYDevice.py` | `.docs/fluxCore/device/SCRCPYDevice.md` | ADB-backed SCRCPYDevice |

## 3. Core Workflows & Data Flow
Discovery client creates SCRCPYDevice(ident=serial). On demand (or explicitly), updateInfo shells adb for size and model. Instance is serialized into InitializeDeviceList / DeviceAdded messages.
