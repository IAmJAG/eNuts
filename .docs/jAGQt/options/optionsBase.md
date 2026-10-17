## Overview & Design Context
Base serializable named options. Subclasses add domain fields. Not retained by hosts after apply.

* **Design Decision:** Path resolution uses `utilities.io.getConfigPath`; I/O is external.

---

## Classes

### `OptionsBase`
- **Purpose:** Shared Name / Version / Description and theme-relative path resolution.
- **Methods:**
  - `resolvePath(themeName)` -> Absolute path to `options/<Name>.json` under that theme.
- **Properties:**
  - `Name` — file identity.
  - `Version` — schema version.
  - `Description` — optional metadata.

---

## Constants & Globals

### `C_OPTIONS_SUBDIR`
- **Type:** `str`
- **Value / Description:** `"options"` subfolder under a theme directory.

### `C_THEMES_SUBDIR`
- **Type:** `str`
- **Value / Description:** `"themes"` under `config/`.

## Sample Usage

```python
from jAGQt.options import OptionsBase

base = OptionsBase(name="SideBar", version=1)
path = base.resolvePath("dark")
```
