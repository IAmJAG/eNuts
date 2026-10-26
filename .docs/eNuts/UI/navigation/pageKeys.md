## Overview & Design Context
Canonical page-id constants and device page-key helpers for navigation and the page stack. Keys are the only identity used for `Page.Id`, menu `pageKey` properties, and `WorkSpace` lookups.

---

## Constants & Globals

### `PAGE_DASHBOARD` / `PAGE_DEVICES` / `PAGE_TOOLS` / `PAGE_ANNOTATOR` / `PAGE_KG_RECORDER` / `PAGE_SETTINGS`
- **Type:** `str`
- **Value / Description:** Stable page ids (`"dashboard"`, `"devices"`, …). Used as dict keys in `PAGE_AND_MENU` and as `Page(..., id=...)`.

### `G_DEVICE_KEY_PREFIX` / `G_DEVICE_NONE`
- **Type:** `str`
- **Value / Description:** Prefix `"device:"` and sentinel `"device:none"` for dynamic device pages.

---

## Functions

### `devicePageKeyFromId`
- **Arguments:** `deviceId` (str)
- **Returns:** `str` — `device:<id>` or `G_DEVICE_NONE`
- **Behavior:** Builds a stable stack/menu key from a device serial.

### `devicePageKey`
- **Arguments:** `nameOrId` (str)
- **Returns:** `str`
- **Behavior:** Same as above; treats empty / "(no devices)" as none.

### `serialFromPageKey`
- **Arguments:** `key` (str)
- **Returns:** `str | None`
- **Behavior:** Inverse of device key helpers.

## Sample Usage

```python
from eNuts.UI.navigation import PAGE_KG_RECORDER, devicePageKeyFromId

page = buildKGRecorderPage(PAGE_KG_RECORDER)
key = devicePageKeyFromId("emulator-5554")
```
