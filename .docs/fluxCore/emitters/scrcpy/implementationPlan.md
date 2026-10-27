# SCRCPYEmitter Bridge Preparation — Implementation Plan

**Status:** Phase A done; B–C pending  
**Branch:** `development`  
**Entity:** `SCRCPYEmitter` (first concrete IPC bridge target)

---

## 1. Goals

1. Event contract uses **SCRCPY** (via `toScrcpy`) / error footprint — not the emitter as the documented event type.
2. Raise **`ON_ERROR`** at strategic failure points with `ScrcpyErrorFootprint`.
3. Define **minimal** IPC message types + payloads (Phase B).
4. Keep domain types under `fluxCore/emitters/scrcpy/`, not `jAGFx.IPC`.
5. Defer frame transport and shared memory.

---

## 2. Event contract

| Event | Arguments |
|-------|-----------|
| AsyncService lifecycle | none |
| `ON_METADATA_UPDATE` | `SCRCPY` via `SCRCPYEmitter.toScrcpy(emitter)` (same object; **no new SCRCPY**) |
| `ON_FRAME` | `iFrame` (in-process only) |
| `ON_ERROR` | `ScrcpyErrorFootprint` (`phase`, `message`, `serial`) |

**ON_ERROR phases:** `initialize.deploy`, `initialize.socket`, `initialize.metadata`, `initialize.codec`, `work`.

---

## 3. Source / docs layout

```text
src/fluxCore/emitters/scrcpy/
  __SCRCPYEmitter.py     # toScrcpy, events, ON_ERROR     [Phase A done]
  __footprint.py         # ScrcpyErrorFootprint           [Phase A done]
  __payloads.py          # ScrcpyInitParams               [Phase B]
  __messages.py          # IPC Message subclasses         [Phase B]
  __bridge.py            # real/proxy bridge              [Phase C]

.docs/fluxCore/emitters/scrcpy/
  implementationPlan.md, requirement.md, implementation.md,
  scrcpyEmitter.md, footprint.md, messages.md (B), bridge.md (C)
```

---

## 4. Minimal IPC protocol (v1) — Phase B

| Message | Direction | Notes |
|---------|-----------|-------|
| `ScrcpyInitializeMessage` | main → client | correlated |
| `ScrcpyStartMessage` / `ScrcpyStopMessage` | main → client | fire-and-forget |
| `ScrcpyMetadataMessage` | client → main | payload: serializable SCRCPY state |
| `ScrcpyErrorMessage` | client → main | `ScrcpyErrorFootprint`; terminal when ending init |

No frames in v1.

---

## 5. Phase status

| Phase | Status |
|-------|--------|
| **A** — `toScrcpy`, metadata/error events | **Done** |
| **B** — payloads + messages | Pending |
| **C** — bridge + smoke | Pending |
| **D** — inventory | Run after each phase |

---

## 6. Non-goals

- `jAGFx.IPC` designed around SCRCPY  
- JSON frame transport  
- Separate `ScrcpyFootprint` class (use `SCRCPY` + `toScrcpy`)  
