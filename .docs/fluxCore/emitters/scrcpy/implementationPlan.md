# SCRCPYEmitter Bridge Preparation — Implementation Plan

**Status:** Plan only (no bridge implementation in this document’s phases until marked)  
**Branch:** `development`  
**Entity:** `SCRCPYEmitter` (first concrete IPC bridge target)

---

## 1. Goals

1. Event contract uses **SCRCPY footprint data only** — never pass `self` / the emitter instance as an event argument.
2. Raise **`ON_ERROR`** at strategic failure points with a serializable error footprint.
3. Define **minimal** IPC message types + payloads for initialize / start / stop + metadata + error.
4. Document source and `.docs` paths before code lands.
5. Defer frame transport and shared memory.

---

## 2. Event contract (ancestors + emitter)

### 2.1 Full event set

| Event | Origin | Arguments (after change) |
|-------|--------|---------------------------|
| `ON_STARTING` | `AsyncService` | none |
| `ON_STARTED` | `AsyncService` | none |
| `ON_STOPPING` | `AsyncService` | none |
| `ON_STOPPED` | `AsyncService` | none |
| `ON_PAUSED` / `ON_RESUMED` | `AsyncService` | none |
| `ON_METADATA_UPDATE` | `SCRCPYEmitter` | **`ScrcpyFootprint`** (not `self`) |
| `ON_FRAME` | `SCRCPYEmitter` | **`iFrame`** (local only; not IPC v1) |
| `ON_ERROR` | `SCRCPYEmitter` | **`ScrcpyErrorFootprint`** |

There is no recursive event bubbling in `Subscription`. “Ancestors” means subscribers may listen to the **full list** above on the same instance because `SCRCPYEmitter` *is* an `AsyncService`.

### 2.2 Rule: no `self` in event args

| Before | After |
|--------|--------|
| `raiseEvent("ON_METADATA_UPDATE", self)` | `raiseEvent("ON_METADATA_UPDATE", footprint)` |
| (no error event) | `raiseEvent("ON_ERROR", errorFootprint)` |

`ON_FRAME` continues to pass the frame object **in-process only**. It is not part of the IPC v1 message set.

### 2.3 Footprint shapes (serializable)

**`ScrcpyFootprint`** — SCRCPY identity + stream geometry (from device fields):

| Field | Source |
|-------|--------|
| `serial` / `id` | `Device.id` / `SCRCPY.serial` |
| `name` | device name after metadata |
| `codecId` | `SCRCPY.codecId` |
| `width` | `SCRCPY.width` |
| `height` | `SCRCPY.height` |

**`ScrcpyErrorFootprint`:**

| Field | Meaning |
|-------|---------|
| `serial` | device id when known |
| `phase` | e.g. `initialize.deploy`, `initialize.socket`, `initialize.metadata`, `initialize.codec`, `work` |
| `message` | human-readable summary |

Optional later: `exceptionType` string. Keep v1 to the three fields above if possible.

---

## 3. Where new files go

### 3.1 Source layout

```text
src/fluxCore/
  emitters/scrcpy/
    __SCRCPYEmitter.py          # MODIFY: events, ON_ERROR, footprint helper
    __init__.py                 # MODIFY: export new public types if needed
    __footprint.py              # NEW: ScrcpyFootprint, ScrcpyErrorFootprint (Serializable)
    __messages.py               # NEW: IPC Message subclasses (minimal set)
    __payloads.py               # NEW: init params + thin payloads if not folded into footprint
    __bridge.py                 # LATER: real/proxy bridge (not in phases 1–2)

  types/interface/emitters/
    __SCRCPYEmitter.py          # MODIFY: document events / initialize signature if needed
    __init__.py                 # export if new interfaces

  devices/__scrcpy.py           # unchanged unless a small snapshot helper fits better here
```

**Placement rationale**

| Artifact | Location | Why |
|----------|----------|-----|
| Footprints | `emitters/scrcpy/__footprint.py` | Domain data for events + IPC; next to emitter |
| IPC message types | `emitters/scrcpy/__messages.py` | First concrete bridge messages stay with the entity, not in `jAGFx.IPC` |
| Payloads (init params) | `emitters/scrcpy/__payloads.py` | Keeps `__messages.py` thin; merge with footprint file if files stay tiny |
| Bridge | `emitters/scrcpy/__bridge.py` | Same package; uses `jAGFx.IPC.Bridge` / `Endpoint` |
| Transport | `jAGFx/IPC/` | Unchanged; no SCRCPY imports in framework layer |

Do **not** put SCRCPY message types under `src/jAGFx/IPC/`.

### 3.2 Documentation layout (mirrors source)

```text
.docs/fluxCore/emitters/scrcpy/
  implementationPlan.md     # this file
  requirement.md            # NEW with first code phase
  implementation.md         # NEW with first code phase
  scrcpyEmitter.md          # NEW: emitter event contract + API notes
  footprint.md              # NEW when __footprint.py lands
  messages.md               # NEW when __messages.py lands
  bridge.md                 # LATER with bridge
```

Also touch:

| Doc | When |
|-----|------|
| `.docs/jAGFx/IPC/IPC.md` | Note first domain bridge is SCRCPY; point to fluxCore scrcpy docs |
| `.docs/jAGFx/IPC/implementation.md` | Cross-link |
| `.docs/inventory.md` | After `updateInventory.py` |

---

## 4. Minimal IPC protocol (v1)

### 4.1 Commands (main → client)

| Message class | Payload | Correlation | Terminal on completion |
|---------------|---------|-------------|-------------------------|
| `ScrcpyInitializeMessage` | `ScrcpyInitParams` (`serial`, `gpuId`, `gpuReady`) | **yes** | success or error ends conversation |
| `ScrcpyStartMessage` | none / empty | no | no required response |
| `ScrcpyStopMessage` | none / empty | no | no required response |

### 4.2 Events (client → main)

| Message class | Payload | Correlation |
|---------------|---------|-------------|
| `ScrcpyMetadataMessage` | `ScrcpyFootprint` | optional: same id as initialize |
| `ScrcpyErrorMessage` | `ScrcpyErrorFootprint` | if tied to initialize, same id + **isTerminal=True** |

### 4.3 Explicitly out of v1

- Frame / pixel IPC  
- Pause / resume commands  
- Separate initialize-result message type (metadata + terminal error cover it)  
- Control injection (tap, key) — later  

### 4.4 Initialize conversation (canonical)

```text
Main:  ScrcpyInitializeMessage (correlationId=C, isTerminal=False)
Client: run initialize()
  ok  → ScrcpyMetadataMessage (correlationId=C) then terminal empty/metadata terminal
        OR single Metadata with isTerminal=True
  fail → ScrcpyErrorMessage (correlationId=C, isTerminal=True)
```

Prefer **one** terminal message at the end of initialize (metadata terminal on success, error terminal on failure) to keep correlation maps clean.

---

## 5. Phased implementation

### Phase A — Footprints + emitter events (no IPC yet)

**Code**

| File | Action |
|------|--------|
| `src/fluxCore/emitters/scrcpy/__footprint.py` | **Create** `ScrcpyFootprint`, `ScrcpyErrorFootprint` |
| `src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py` | Build footprint on metadata; `ON_METADATA_UPDATE` passes footprint; add `ON_ERROR` at strategic points; never pass `self` |
| `src/fluxCore/emitters/scrcpy/__init__.py` | Export footprints |
| `src/fluxCore/types/interface/emitters/__SCRCPYEmitter.py` | Note event arg contract if documented there |

**ON_ERROR sites**

1. `initialize`: deploy failure  
2. `initialize`: socket failure  
3. `initialize`: metadata failure  
4. `initialize`: codec context failure  
5. `work`: unexpected exception (not `CancelledError`, not handled `InvalidDataError`)  

After `ON_ERROR`, re-raise or stop so lifecycle remains coherent.

**Docs (same commit group)**

| File | Action |
|------|--------|
| `.docs/fluxCore/emitters/scrcpy/requirement.md` | **Create** |
| `.docs/fluxCore/emitters/scrcpy/implementation.md` | **Create** |
| `.docs/fluxCore/emitters/scrcpy/scrcpyEmitter.md` | **Create** — event table, no-`self` rule |
| `.docs/fluxCore/emitters/scrcpy/footprint.md` | **Create** |

**Acceptance**

- No event passes the emitter instance.  
- Metadata listeners receive `ScrcpyFootprint` only.  
- Forced init failure raises `ON_ERROR` with phase + message.  

---

### Phase B — IPC messages + payloads

**Code**

| File | Action |
|------|--------|
| `src/fluxCore/emitters/scrcpy/__payloads.py` | **Create** `ScrcpyInitParams` (and empty marker if needed) |
| `src/fluxCore/emitters/scrcpy/__messages.py` | **Create** five message subclasses of `jAGFx.IPC.Message` |
| `src/fluxCore/emitters/scrcpy/__init__.py` | Export messages/payloads |

**Message subclasses**

```text
ScrcpyInitializeMessage
ScrcpyStartMessage
ScrcpyStopMessage
ScrcpyMetadataMessage
ScrcpyErrorMessage
```

Each sets payload type appropriately; use `isTerminal` on the initialize completion path as in §4.4.

**Docs**

| File | Action |
|------|--------|
| `.docs/fluxCore/emitters/scrcpy/messages.md` | **Create** |
| `.docs/fluxCore/emitters/scrcpy/implementation.md` | Update mapping |
| `.docs/jAGFx/IPC/IPC.md` | Short cross-link: first domain messages live under fluxCore scrcpy |

**Acceptance**

- Messages encode/decode via existing serializer (smoke test optional).  
- Type of each message is distinct for `Bridge.messageHandlers` keys.  

---

### Phase C — Bridge (after A+B)

**Code**

| File | Action |
|------|--------|
| `src/fluxCore/emitters/scrcpy/__bridge.py` | **Create** real-side + proxy-side (or one class, two roles) |
| `.test/smoke/ipc/` or `.test/smoke/scrcpy/` | Smoke: register handlers, initialize conversation mock |

**Docs**

| File | Action |
|------|--------|
| `.docs/fluxCore/emitters/scrcpy/bridge.md` | **Create** |
| `requirement.md` / `implementation.md` | Bridge FRs |

**Out of scope for C unless requested:** process spawn host, frame IPC, eNuts UI wiring.

---

### Phase D — Housekeeping

- Run `.scripts/updateInventory.py`  
- Final pass on `.docs/jAGFx/IPC/implementationPlan.md` status if needed  

---

## 6. Documentation plan (summary)

| Document | Owner phase | Content |
|----------|-------------|---------|
| `implementationPlan.md` | now | This plan |
| `requirement.md` | A | FRs: no self, ON_ERROR sites, footprint fields, minimal IPC set |
| `implementation.md` | A→C | Module map, workflows |
| `scrcpyEmitter.md` | A | Events, lifecycle, initialize/start/stop |
| `footprint.md` | A | `ScrcpyFootprint`, `ScrcpyErrorFootprint` |
| `messages.md` | B | Message types, correlation rules |
| `bridge.md` | C | Real vs proxy, handler registration |
| `jAGFx/IPC/IPC.md` | B | Cross-link only |

Every new source directory under `emitters/scrcpy/` that introduces a module should keep `.docs/fluxCore/emitters/scrcpy/` in sync in the **same commit group** (project rule).

---

## 7. Execution order

```text
A  footprints + emitter event changes + emitter docs
B  payloads + message types + messages docs + IPC cross-link
C  bridge + bridge docs + smoke
D  inventory
```

Do not start C until A and B are merged and consistent with type-keyed handlers.

---

## 8. Non-goals (reminders)

- Designing `jAGFx.IPC` around SCRCPY  
- JSON frame transport  
- Expanding command set beyond initialize / start / stop in v1  
