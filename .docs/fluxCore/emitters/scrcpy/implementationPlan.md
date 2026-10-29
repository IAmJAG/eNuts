# SCRCPYEmitter Bridge — Implementation Plan

**Status:** Phase A–B done; C pending  
**Branch:** `development`  
**Purpose:** Control and observe `SCRCPYEmitter` across processes via `jAGFx.IPC` without sharing the live emitter object.

---

## Phase status

| Phase | Status |
|-------|--------|
| **A** — toScrcpy, SCRCPYError, async events | **Done** |
| **B** — payloads + messages | **Done** |
| **C** — bridge + smoke | Pending |
| **D** — `updateInventory.py` | After each code phase |

---

## Layout

```text
src/fluxCore/emitters/scrcpy/
  __SCRCPYEmitter.py     # A
  __footprint.py         # SCRCPYError — A
  __payloads.py          # ScrcpyInitParams — B
  __messages.py          # five Message subclasses — B
  __bridge.py            # C pending
  __init__.py
```

---

## Phase B message set (done)

| Message | Direction | Payload | Correlation |
|---------|-----------|---------|-------------|
| `ScrcpyInitializeMessage` | main → client | `ScrcpyInitParams` | yes |
| `ScrcpyStartMessage` | main → client | none | no |
| `ScrcpyStopMessage` | main → client | none | no |
| `ScrcpyMetadataMessage` | client → main | base `SCRCPY` | optional |
| `ScrcpyErrorMessage` | client → main | `SCRCPYError` | optional; terminal on failed init |

---

## Phase C — bridge (pending)

| Path | Action |
|------|--------|
| `__bridge.py` | Real + proxy; type handlers; Endpoint registration |
| smoke tests | Initialize conversation |
| `bridge.md` | Update from plan to implementation |
