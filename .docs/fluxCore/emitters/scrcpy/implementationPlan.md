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

IPC **control** path for SCRCPY is complete: typed messages, bridges, default-route send, correlated initialize, smoke without ADB.

## Follow-on track (frames + UI)

Cross-process **GPU frame plane** and K&G Recorder `GLImage` presentation:

→ **`.docs/eNuts/recorder/streamPipeline/implementationPlan.md`** (P0–P7)

| Deferred item | Now owned by |
|---------------|--------------|
| Frame transport (not Message queues) | streamPipeline P1–P3 |
| Process host / client spawn | streamPipeline P4 |
| eNuts UI / KG Recorder | streamPipeline P5–P6 |
| Control injection over bridge | Still later (optional) |
