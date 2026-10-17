## Overview & Design Context
Scrollable SideBar menu: header rows with optional one-level leaves.

* **Selection:** Owned on the item (`Selected` / QSS `selected`). Menu applies **single select on click by default** (`SelectOnClick`). Disable and handle `itemClicked` / `selectionRequested` for custom policy.
* **No `ancestorSelected`:** Use `ParentItem` / `menu.parentOf(item)` to trace ancestors.
* **Expand / accordion:** Not enforced by the menu; set `item.Expanded` from the app or a later policy.
* **SideBar.State:** Menu does not listen; Title/theme handle width.

---

## Classes

### `SideBarMenu`
- **Signals:** `itemClicked(item)`, `selectionChanged(item|None)`
- **Methods:** `addItem`, `clear`, `selectItem`, `parentOf`
- **Properties:** `Items`, `SelectedItem`, `SelectOnClick`

### `SideBarMenuItem`
- **Signals:** `clicked`, `selectionRequested`, `toggled`
- **Properties:** `Role`, `Caption`, `Expanded`, `Selected`, `Children`, `ParentItem`

### `eSideBarMenuRole`
- `Header`, `Leaf`

## Sample Usage

```python
menu = SideBarMenu()
devices = menu.addItem("Devices")
devices.addChild("Connected")
menu.itemClicked.connect(onClick)       # always
menu.selectionChanged.connect(onSelect) # default selection path
# menu.SelectOnClick = False            # app owns selection via selectItem()
```
