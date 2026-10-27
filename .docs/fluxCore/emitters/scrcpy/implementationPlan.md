# SCRCPYEmitter Bridge Preparation — Implementation Plan

**Status:** Phase A done; B–C pending  
**Branch:** `development`

## Event contract

| Event | Arguments |
|-------|-----------|
| `ON_METADATA_UPDATE` | base `SCRCPY` from `toScrcpy` |
| `ON_FRAME` | `iFrame` |
| `ON_ERROR` | `phase`, `message`, `serial` (strings) |

`toScrcpy` constructs `SCRCPY(...)` and copies attributes. No footprint class.

## Layout

```text
src/fluxCore/emitters/scrcpy/
  __SCRCPYEmitter.py     # toScrcpy, events, ON_ERROR
  __payloads.py / __messages.py / __bridge.py   # B/C
```

## Phases

| Phase | Status |
|-------|--------|
| A | **Done** |
| B messages | Pending |
| C bridge | Pending |
