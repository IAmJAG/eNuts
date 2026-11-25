# Implementation Details

## 1. Architecture Overview
Module-level `deviceWatcher` is the ProcessHost worker. It owns discovery and heartbeat tasks, dispatches messages via `ownDispatch`. Devices are SCRCPYDevice instances.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/services/clients/deviceManager/__deviceManager.py` | `.docs/eNuts/services/clients/deviceManager/deviceManager.md` | Discovery + heartbeat worker |
| `src/eNuts/services/clients/deviceManager/message/*.py` | (see message files) | Device* message types |

## 3. Core Workflows & Data Flow
ProcessHost.start("deviceManager") → child runs deviceWatcher → Handshake → parent acks → _discovery + _beat → periodic Device* and Heartbeat messages on shared inbound → parent UI/recorder consume.
