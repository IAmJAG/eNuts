## Overview & Design Context

**Status:** Planned (Phase C — not implemented in source yet).

Bridge binds `SCRCPYEmitter` to a local `jAGFx.IPC.Endpoint`.

| Role | Process | Responsibility |
|------|---------|----------------|
| Real | client | Owns emitter; handles Initialize/Start/Stop; emits Metadata/Error messages |
| Proxy | main | Sends commands; receives Metadata/Error; no live sockets |

Machinery is the same (`Bridge` base + type-keyed handlers). Only ownership of the real emitter differs.

---

## Planned file

| Source | Role |
|--------|------|
| `__bridge.py` | Real and/or proxy bridge class(es) |

Smoke tests under `.test/smoke/scrcpy/` or `.test/smoke/ipc/` after implementation.
