# Requirements — SCRCPY emitter / bridge

## Done (A–C)

- **FR-A:** `toScrcpy`, `SCRCPYError`, `asyncRaiseEvent`.
- **FR-B:** Message types under `emitters/scrcpy/`.
- **FR-C1:** `ScrcpyRealBridge` owns emitter; Initialize/Start/Stop; Metadata/Error out.
- **FR-C2:** `ScrcpyProxyBridge` commands + receive surface; correlated initialize.
- **FR-C3:** Smoke under `.test/smoke/scrcpy/` with stub emitter (no ADB).

## Deferred

Frame transport, shared memory, process host, UI.
