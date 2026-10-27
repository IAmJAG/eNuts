## Overview & Design Context

**Metadata footprint** is a base `SCRCPY` produced by `SCRCPYEmitter.toScrcpy` — construct `SCRCPY`, copy attributes, return it. There is no separate metadata footprint class.

**Error footprint** remains `ScrcpyErrorFootprint` for `ON_ERROR` (errors are not a SCRCPY).

---

## Metadata — base `SCRCPY`

| Field | Source on emitter |
|-------|-------------------|
| `id` / `serial` | `emitter.id` |
| `name` | `emitter.name` |
| `codecId` | `emitter.codecId` |
| `width` / `height` | `emitter.width` / `height` |

`type(toScrcpy(emitter)) is SCRCPY` — never `SCRCPYEmitter`.

---

## Classes

### `ScrcpyErrorFootprint`

- **Purpose:** Serializable error detail for `ON_ERROR`.
- **Properties:** `phase`, `message`, `serial`

| Phase | When |
|-------|------|
| `initialize.deploy` | Server deploy failed |
| `initialize.socket` | Video/control socket failed |
| `initialize.metadata` | Header/metadata parse failed |
| `initialize.codec` | Codec context failed |
| `work` | Unexpected stream loop error |
