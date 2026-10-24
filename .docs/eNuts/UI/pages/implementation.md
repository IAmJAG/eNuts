# Implementation Details

## 1. Architecture Overview
- **View:** `buildKGRecorderPage` → `Page` + `CaptureImage` + config strip + event list + CommandBar.
- **Controller:** `KGRecorder` (`src/eNuts/application/recorder/__kgRecorder.py`), contract `iKGRecorder`.
- **Wiring:** Shell creates `KGRecorder`, binds it to the kg-recorder page after WorkSpace construction, connects CommandBar buttons and view signals.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/UI/pages/__kgRecorderPage.py` | `.docs/eNuts/UI/pages/kgRecorderPage.md` | Page factory |
| `src/eNuts/UI/widgets/__captureImage.py` | `.docs/eNuts/UI/widgets/captureImage.md` | Event-emitting Image |
| `src/eNuts/application/recorder/__kgRecorder.py` | `.docs/eNuts/application/recorder/kgRecorder.md` | Session controller |
| `src/eNuts/types/interface/recorder/__iKGRecorder.py` | `.docs/eNuts/types/interface/recorder/iKGRecorder.md` | Contract |

## 3. Core Workflows & Data Flow
1. Shell constructs `KGRecorder` and WorkSpace.
2. Shell binds recorder to `PAGE_KG_RECORDER` page (capture signals, CommandBar, status/list).
3. User selects device (combo) → `setDeviceId`.
4. Start → Recording state, focus capture, collect key/pointer events with relative timestamps.
5. Stop → Idle; events remain in memory.
6. Clear → discard session.
7. Save / Open → stubs until file naming convention and MP4 encoder are decided (intent-dependent).

## 4. Deferred
- Live device-list subscription for the combo.
- MP4 continuous capture from stream frames.
- Event file schema (must complement Policy action parameters).
- Coordinate normalization to stream resolution.
- Dockable event panel.
- CommandBar shortcuts.
- File naming / directory convention for paired artefacts.
