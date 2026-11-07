# AI Handoff — eNuts (development)

**Branch:** `development`  
**Updated:** 2026-11-07  
**Scope:** IAmJAG/eNuts only

## Architecture locks

- **Shell** (`src/eNuts/application/__shell.py`): owns `DeviceManager` + `QSettings` + WorkSpace. Does **not** own recording controller.
- **DeviceManager** lives under `src/eNuts/services/device/` (not `application/device`). Docs: `.docs/eNuts/services/device/`.
- **KG Recorder page** (`src/eNuts/UI/pages/__kgRecorder.py`): owns Idle|Recording UI, device combo, inject, `LocalDeviceStream` preview, and session start/stop.
- **KGRecorderService** (`src/eNuts/services/recorder/`): every emitter `ON_FRAME` → `video.h264`; key/pointer → `session.json`. Protocol: `iKGRecorderService`.
- Application-level recorder package / Shell-bound controller: **removed**.

## Import map (current)

```python
from eNuts.services.device import (
    DeviceManager,
    DEVICE_ADDED_EVENT,
    DEVICE_INITIALIZED_EVENT,
    DEVICE_REMOVED_EVENT,
)
from eNuts.services.recorder import KGRecorderService
from eNuts.types.interface.services.recorder import iKGRecorderService
from eNuts.types.interface.services.device import iDeviceManager
```

Stale (do not use):

- `eNuts.application.device`
- `eNuts.application.recorder`
- `iKGRecorder` (page-level protocol removed)

## Docs layout (path-mirrored)

| Source | Docs |
|--------|------|
| `src/eNuts/application/__shell.py` | `.docs/eNuts/application/shell/` |
| `src/eNuts/services/device/` | `.docs/eNuts/services/device/` |
| `src/eNuts/services/recorder/` | `.docs/eNuts/services/recorder/` |
| `src/eNuts/UI/pages/__kgRecorder.py` | `.docs/eNuts/UI/pages/kgRecorderPage.md` |
| `src/fluxCore/stream/` | `.docs/fluxCore/stream/` |

Removed stale tree: `.docs/eNuts/application/device/`.

Orphan design notes formerly under `.docs/eNuts/recorder/streamPipeline/` describe fluxCore stream/ring work; content belongs under `.docs/fluxCore/stream/` (no `src/eNuts/recorder/` package).

## Stream / record mental model

- **Preview:** `LocalDeviceStream` + ring + present (may skip).
- **Record:** `KGRecorderService` subscribes emitter `ON_FRAME` directly (no skip).
- One emitter; no dual-emitter preview/capture split.

## Deferred

- Save/Open UX and naming for session artefacts.
- Precise image-fit transform / coordinate polish.
- Ring slot state machine + ImageProcessor-on-ring (see fluxCore stream notes).
- MP4 remux (v1 = elementary h264 + JSON events).

## Before commit

Run `.scripts/updateInventory.py` so `.docs/inventory.md` matches the tree.
