## Overview & Design Context

Error snapshot for `ON_ERROR`. Metadata uses `SCRCPY` via `SCRCPYEmitter.toScrcpy`, not a separate metadata footprint type.

---

## Classes

### `ScrcpyErrorFootprint`

- **Purpose:** Serializable error detail for IPC-ready event args.
- **Properties:** `phase`, `message`, `serial`

| Phase | When |
|-------|------|
| `initialize.deploy` | Server deploy failed |
| `initialize.socket` | Video/control socket failed |
| `initialize.metadata` | Header/metadata parse failed |
| `initialize.codec` | Codec context failed |
| `work` | Unexpected stream loop error |
