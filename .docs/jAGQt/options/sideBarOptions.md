## Overview & Design Context
Serializable settings for SideBar widths and optional width-animation class name.

---

## Classes

### `SideBarOptions`
- **Purpose:** Defaults and theme-loadable chrome metrics for SideBar.
- **Properties:**
  - `expandedWidth` / `collapsedWidth` — positive ints.
  - `animation` — fully qualified class name or `None`.

---

## Constants & Globals

### `C_DEFAULT_EXPANDED_WIDTH`
- **Type:** `int`
- **Value / Description:** `200`

### `C_DEFAULT_COLLAPSED_WIDTH`
- **Type:** `int`
- **Value / Description:** `48`

## Sample Usage

```python
from jAGQt.options import SideBarOptions

opts = SideBarOptions(
    animation="jAGQt.animations.RubberBand",
    expandedWidth=200,
    collapsedWidth=48,
)
```
