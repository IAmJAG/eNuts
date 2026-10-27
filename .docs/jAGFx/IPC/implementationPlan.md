# IPC Implementation Plan

**Status:** Phases 1–5 complete on `development`  
**Scope:** Message extensions, `Endpoint`, Bridge registration and correlation  
**Out of scope:** payload-kind conventions beyond provisional helper, shared-memory / large binary transport

---

## Phase overview

| Phase | Goal | Status |
|-------|------|--------|
| **0** | Docs aligned | Done |
| **1** | Extend `Message` (`timestamp`, `isTerminal`) | **Done** |
| **2** | `Endpoint` skeleton (start/stop, async `send`, tasks) | **Done** |
| **3** | Bridge contract + registration + kind dispatch | **Done** |
| **4** | Correlation + terminal lifecycle | **Done** |
| **5** | Package exports + docs sync | **Done** |

---

## Delivered modules

| Path | Role |
|------|------|
| `src/jAGFx/IPC/__message.py` | Message + timestamp + isTerminal |
| `src/jAGFx/IPC/__endpoint.py` | Endpoint |
| `src/jAGFx/IPC/__bridge.py` | Bridge base |
| `src/jAGFx/IPC/__IOQueue.py` | Transport adapter |
| `src/jAGFx/types/interface/communication/__message.py` | `iMessage` |
| `src/jAGFx/types/interface/communication/__endpoint.py` | `iEndpoint` |
| `src/jAGFx/types/interface/communication/__bridge.py` | `iBridge` |

---

## Follow-ups (not in this plan)

| Item | When |
|------|------|
| Concrete domain bridges | Application layers |
| Kind string conventions | First concrete Bridge |
| Shared memory / large binary | Separate plan |
| Automated tests under `.test/` | Recommended next |
| Run `.scripts/updateInventory.py` | Before next formal commit batch if inventory is stale |
