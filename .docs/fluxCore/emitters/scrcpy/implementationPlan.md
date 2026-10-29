# SCRCPYEmitter Bridge — Implementation Plan

**Status:** Phase A done; B–C pending  
**Branch:** `development`  
**Purpose:** Control and observe `SCRCPYEmitter` across processes via `jAGFx.IPC` without sharing the live emitter object.

---

## 1. Why

| Side | Role |
|------|------|
| Client process | Owns real `SCRCPYEmitter` (ADB, sockets, codec, frame loop) |
| Main process | Proxy surface: initialize / start / stop; receive metadata and errors |

Phase A makes the real emitter’s events snapshot-safe. Phase B defines wire messages. Phase C implements real/proxy bridges on `Endpoint`.

**Not in scope yet:** frame / pixel IPC, shared memory, process host UI wiring, designing `jAGFx.IPC` around scrcpy.

---

## 2. Event contract (Phase A — done)

| Event | Payload | Notes |
|-------|---------|--------|
| AsyncService lifecycle | — | `ON_STARTING` / `ON_STARTED` / `ON_STOPPING` / `ON_STOPPED` / pause/resume |
| `ON_METADATA_UPDATE` | base `SCRCPY` | via `SCRCPYEmitter.toScrcpy` |
| `ON_FRAME` | `iFrame` | in-process only |
| `ON_ERROR` | `SCRCPYError` | `phase`, `message`, `serial` |
| `ON_INITIALIZED` | codec context | local only |

All `SCRCPYEmitter`-raised events use **`await asyncRaiseEvent`** (aligned with `AsyncSubscription`).

### `toScrcpy`

```python
@classmethod
def toScrcpy(cls, emitter: SCRCPYEmitter) -> SCRCPY:
    scrcpy = SCRCPY(serial=str(emitter.id), name=emitter.name)
    scrcpy.update(codecId=emitter.codecId, width=emitter.width, height=emitter.height)
    return scrcpy  # type is SCRCPY, not SCRCPYEmitter
```

### `ON_ERROR` phases

| Phase | When |
|-------|------|
| `initialize.deploy` | Server deploy failed |
| `initialize.socket` | Video/control socket failed |
| `initialize.metadata` | Header parse failed |
| `initialize.codec` | Codec context failed |
| `work` | Unexpected stream-loop error |

After `ON_ERROR`, the original exception still propagates. `CancelledError` and handled `InvalidDataError` do not raise `ON_ERROR`.

---

## 3. Source / docs layout

```text
src/fluxCore/emitters/scrcpy/
  __SCRCPYEmitter.py     # Phase A done
  __footprint.py         # SCRCPYError — Phase A done
  __payloads.py          # Phase B
  __messages.py          # Phase B
  __bridge.py            # Phase C
  __init__.py

.docs/fluxCore/emitters/scrcpy/
  implementationPlan.md  # this file
  requirement.md
  implementation.md
  scrcpyEmitter.md
  footprint.md           # SCRCPYError module doc
  messages.md            # Phase B
  bridge.md              # Phase C
```

Domain types stay under `fluxCore/emitters/scrcpy/`. Do **not** put SCRCPY messages under `src/jAGFx/IPC/`.

---

## 4. Phase B — IPC messages (pending)

### Files to hit

| Path | Action |
|------|--------|
| `src/fluxCore/emitters/scrcpy/__payloads.py` | **Create** — `ScrcpyInitParams` |
| `src/fluxCore/emitters/scrcpy/__messages.py` | **Create** — five `Message` subclasses |
| `src/fluxCore/emitters/scrcpy/__init__.py` | Export payloads + messages |
| `.docs/fluxCore/emitters/scrcpy/messages.md` | **Create** |
| `.docs/fluxCore/emitters/scrcpy/implementation.md` | Update module map |
| `.docs/jAGFx/IPC/IPC.md` | Short cross-link only |

### Message set (minimal)

| Message | Direction | Payload | Correlation |
|---------|-----------|---------|-------------|
| `ScrcpyInitializeMessage` | main → client | `ScrcpyInitParams` | yes; terminal on completion |
| `ScrcpyStartMessage` | main → client | none | no |
| `ScrcpyStopMessage` | main → client | none | no |
| `ScrcpyMetadataMessage` | client → main | base `SCRCPY` | optional (init id) |
| `ScrcpyErrorMessage` | client → main | `SCRCPYError` | if tied to init: same id + terminal |

`ScrcpyInitParams`: `serial`, `gpuId=0`, `gpuReady=True`.

---

## 5. Phase C — bridge (pending)

| Path | Action |
|------|--------|
| `src/fluxCore/emitters/scrcpy/__bridge.py` | **Create** real + proxy (or one class, two roles) |
| `.test/smoke/scrcpy/` or `.test/smoke/ipc/` | Smoke: register, initialize conversation |
| `.docs/fluxCore/emitters/scrcpy/bridge.md` | **Create** |

Real side owns `SCRCPYEmitter`, maps commands → emitter calls, events → outbound messages. Proxy side sends commands and surfaces metadata/errors. Both register on local `Endpoint`.

---

## 6. Phase status

| Phase | Status |
|-------|--------|
| **A** — toScrcpy, SCRCPYError, async events | **Done** |
| **B** — payloads + messages | Pending |
| **C** — bridge + smoke | Pending |
| **D** — `updateInventory.py` | After each code phase |
