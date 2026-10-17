## Overview & Design Context
Scrollable SideBar menu: top-level header rows with optional one-level leaf children. Single selection; parent of a selected leaf gets `ancestorSelected`. No chevron; header expand is show/hide of the body.

Plug into SideBar via `sideBar.setContent(menu)` / `sideBar.Content = menu`.

---

## Classes

### `SideBarMenu`
- **Purpose:** Host list of `SideBarMenuItem` headers.
- **Methods:**
  - `addItem(item|str, icon=None, role=Header)` -> `SideBarMenuItem`
  - `clear()`
- **Properties:** `Items`, `SelectedItem`
- **Signals:** `selectionChanged(item|None)`

### `SideBarMenuItem`
- **Purpose:** One row (header or leaf).
- **Methods:** `addChild(item|str, icon=None)`, `clearChildren()`, `attachBodyTo(layout)`
- **Properties:** `Role`, `Caption`, `Expanded`, `Selected`, `AncestorSelected`, `Children`
- **Signals:** `clicked`, `toggled`, `selectionRequested`

### `eSideBarMenuRole`
- **Members:** `Header`, `Leaf`

## Sample Usage

```python
from jAGQt.widgets.SideBar import (
    SideBar, eSideBarState, SideBarMenu, SideBarMenuItem, eSideBarMenuRole,
)

menu = SideBarMenu()
devices = menu.addItem("Devices")
devices.addChild("Connected")
devices.addChild("History")
menu.addItem("Settings", role=eSideBarMenuRole.Header)

sidebar.Content = menu
menu.selectionChanged.connect(lambda item: ...)
```
