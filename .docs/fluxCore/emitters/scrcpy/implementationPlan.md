# SCRCPYEmitter Bridge Preparation — Implementation Plan

**Status:** Phase A done (toScrcpy = base SCRCPY snapshot); B–C pending  
**Branch:** `development`  
**Entity:** `SCRCPYEmitter`

---

## 1. Goals

1. Metadata footprint = **base `SCRCPY`** built by `toScrcpy` (construct + copy attributes; not the emitter).
2. **`ON_ERROR`** with `ScrcpyErrorFootprint` at strategic sites.
3. Minimal IPC messages (Phase B).
4. Domain types under `fluxCore/emitters/scrcpy/`, not `jAGFx.IPC`.
5. Defer frame IPC.

---

## 2. Event contract

| Event | Arguments |
|-------|-----------|
| AsyncService lifecycle | none |
| `ON_METADATA_UPDATE` | **base `SCRCPY`** from `toScrcpy` (`type is SCRCPY`, not `SCRCPYEmitter`) |
| `ON_FRAME` | `iFrame` (local only) |
| `ON_ERROR` | `ScrcpyErrorFootprint` |

```python
@classmethod
def toScrcpy(cls, emitter: SCRCPYEmitter) -> SCRCPY:
    scrcpy = SCRCPY(serial=str(emitter.id), name=emitter.name)
    scrcpy.update(codecId=emitter.codecId, width=emitter.width, height=emitter.height)
    return scrcpy
```

No `ScrcpyFootprint` class — do not reinvent `SCRCPY`.

---

## 3. Layout

```text
src/fluxCore/emitters/scrcpy/
  __SCRCPYEmitter.py     # toScrcpy, events, ON_ERROR     [A done]
  __footprint.py         # ScrcpyErrorFootprint only      [A done]
  __payloads.py / __messages.py / __bridge.py             [B/C]
```

---

## 4. Phase status

| Phase | Status |
|-------|--------|
| **A** | **Done** |
| **B** messages | Pending |
| **C** bridge | Pending |
