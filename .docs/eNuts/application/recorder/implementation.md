# Implementation Details

## 1. Architecture Overview
`KGRecorder` always injects capture-surface keys/gestures to the selected device via fluxCore (`InjectKeyPress`/`InjectKeyRelease`, `Touch`). When Recording, the same successful actions are logged to the session. Device combo is disabled while Recording.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/application/recorder/__kgRecorder.py` | `.docs/eNuts/application/recorder/kgRecorder.md` | Controller |
| `src/eNuts/types/interface/recorder/__iKGRecorder.py` | `.docs/eNuts/types/interface/recorder/iKGRecorder.md` | Contract |
| `src/eNuts/application/__shell.py` | `.docs/eNuts/application/shell/shell.md` | Owner / wiring |

## 3. Core Workflows
1. Shell: create `deviceManager`, create `KGRecorder`, `setDeviceManager(mgr)`, bind page.
2. Device list events → combo refresh (skipped while Recording).
3. Combo / `setDeviceId` → stream attach (blocked while Recording).
4. Capture events → inject to control socket → if Recording and inject ok → session log.
5. Pointer move only when dragging (`buttons != NoButton`).
6. Widget coords → image fit transform → device resolution before `Touch`.

## 4. Deferred / Missing
- `LocalDeviceStream` / `src/eNuts/application/stream/__deviceStream.py` is referenced by `KGRecorder` but is **missing** from the development tree (inventory still lists it).
- MP4 writer from SCRCPY frames.
- Event file format and on-disk naming.
- Extended Qt→Android key map beyond the practical subset.
