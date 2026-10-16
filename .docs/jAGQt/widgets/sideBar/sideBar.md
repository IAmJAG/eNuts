## Overview & Design Context
Fixed-width sidebar host. Places a `SideBarHeader` at the top and a stretch below (no content body widget).

* **Design Decision:** Public package surface is `SideBar` and `eSideBarState` only. Item/header live under `SideBar.components` and are not re-exported. Icons dict is required.

---

## Classes

### `SideBar`
- **Purpose:** Application sidebar shell with header and stretch placeholder.
- **Methods:**
  - `_wInitializeUI()` -> Fixed width, stylesheet, header + stretch layout.
- **Properties:**
  - `Header` — internal `SideBarHeader` instance.
  - `Title` / `Description` — forwarded to the header.
  - `State` — forwarded to the header statefull icon.

---

## Sample Usage

```python
from jAGQt.widgets.SideBar import SideBar, eSideBarState

sidebar = SideBar(
    icons={
        eSideBarState.Expanded: "assets/icons/logo.png",
        eSideBarState.Collapsed: "assets/icons/logo.png",
    },
    title="eNuts",
    description="Navigation",
)
sidebar.State = eSideBarState.Collapsed
```
