## Overview & Design Context
Scrollable SideBar menu: header rows with optional one-level leaves.

* **Selection:** Owned on the item (`Selected`). Menu default: single select on click (`SelectOnClick`).
* **Header click (default):** if the header has children, toggle expand/collapse, then selection + `clicked`.
* **Leaf click:** selection + `clicked` only.
* **No `ancestorSelected`:** use `ParentItem` / `menu.parentOf(item)`.
* **Accordion:** not enforced; app may close siblings on `toggled` / `itemClicked`.
* **SideBar.State:** menu does not listen; Title/theme handle width.

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
# click Devices → expands/collapses + selects (default)
menu.selectionChanged.connect(onSelect)
```
