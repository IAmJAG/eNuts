## Overview & Design Context

**Status:** Planned (Phase B — not implemented in source yet).

IPC message types for the first domain bridge. Live under `src/fluxCore/emitters/scrcpy/`, not under `jAGFx.IPC`.

---

## Planned payloads

### `ScrcpyInitParams`

- **Fields:** `serial: str`, `gpuId: int = 0`, `gpuReady: bool = True`

---

## Planned message classes

| Class | Direction | Payload | Correlation |
|-------|-----------|---------|-------------|
| `ScrcpyInitializeMessage` | main → client | `ScrcpyInitParams` | yes |
| `ScrcpyStartMessage` | main → client | none | no |
| `ScrcpyStopMessage` | main → client | none | no |
| `ScrcpyMetadataMessage` | client → main | base `SCRCPY` | optional |
| `ScrcpyErrorMessage` | client → main | `SCRCPYError` | optional; terminal when ending init |

Initialize completion: terminal metadata on success, or terminal error on failure (same `correlationId`).

**Out of v1:** frame messages, pause/resume commands, control injection.

---

## Files (when implemented)

| Source | Role |
|--------|------|
| `__payloads.py` | `ScrcpyInitParams` |
| `__messages.py` | five `Message` subclasses |
