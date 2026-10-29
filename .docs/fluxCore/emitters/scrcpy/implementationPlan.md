# SCRCPYEmitter Bridge — Implementation Plan

**Status:** Phases A–D done  
**Branch:** `development`

| Phase | Status |
|-------|--------|
| A — emitter events / toScrcpy / SCRCPYError | **Done** |
| B — payloads + messages | **Done** |
| C — real/proxy bridge + smoke | **Done** |
| D — inventory + doc close-out | **Done** |

```text
src/fluxCore/emitters/scrcpy/
  __SCRCPYEmitter.py  __footprint.py  __payloads.py  __messages.py  __bridge.py
.test/smoke/scrcpy/test_scrcpy_bridge.py
```

## Closed for this track

IPC domain path for SCRCPY is complete: typed messages, bridges, default-route send, correlated initialize, smoke without ADB.

## Deferred (new tracks)

| Track | Notes |
|-------|--------|
| Frame / shared-memory transport | Not on Message queues |
| Process host / client spawn | Wire Endpoint pair into app process model |
| eNuts UI integration | Proxy on main window / KG recorder |
| Control injection over bridge | Optional later commands |
