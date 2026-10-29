# SCRCPYEmitter Bridge — Implementation Plan

**Status:** Phases A–C done  
**Branch:** `development`

| Phase | Status |
|-------|--------|
| A | **Done** |
| B | **Done** |
| C — bridge + smoke | **Done** |

```text
src/fluxCore/emitters/scrcpy/
  __SCRCPYEmitter.py  __footprint.py  __payloads.py  __messages.py  __bridge.py
.test/smoke/scrcpy/test_scrcpy_bridge.py
```

Deferred: frame IPC, shared memory, process host, UI.
