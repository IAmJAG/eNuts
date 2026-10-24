# Implementation Details

## 1. Architecture Overview
`KGRecorder` (QObject) holds `_state`, `_deviceId`, `_events`, binds to page `_captureImage`, and drives status/event list via signals. Shell wires CommandBar buttons to controller methods.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/application/recorder/__kgRecorder.py` | `.docs/eNuts/application/recorder/kgRecorder.md` | Controller |
| `src/eNuts/types/interface/recorder/__iKGRecorder.py` | `.docs/eNuts/types/interface/recorder/iKGRecorder.md` | Contract |

## 3. Core Workflows
See UI pages implementation.md for the end-to-end flow.

## 4. Deferred
- MP4 writer from SCRCPY frames.
- Event file format and on-disk naming.
- Coordinate normalization vs stream resolution.
