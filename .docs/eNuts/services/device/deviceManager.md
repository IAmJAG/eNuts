## Overview & Design Context
**LEGACY / DISCONNECTED.** This documents the previous in-process DeviceManager. It is no longer instantiated by Shell or exported from services. File remains for reference only.

Current device discovery lives in the out-of-process client at `src/eNuts/services/clients/deviceManager/` (see `.docs/eNuts/services/clients/deviceManager/`).

* **Design Decision / Deviation Notes:** Deliberately disconnected 2026-11-24 (commits 26033eb, 3781b31, b499764, 80ae884, 6ea8977). Do not re-enable without explicit redesign.

---

## Classes

### `DeviceManager` (legacy)
- **Purpose:** Former async in-process registry. No longer used.
- **Status:** Disconnected. Events and ensureRunning helpers removed from call sites.

## Sample Usage

```python
# DO NOT USE — disconnected
# from eNuts.services.device import DeviceManager  # removed from exports
```
