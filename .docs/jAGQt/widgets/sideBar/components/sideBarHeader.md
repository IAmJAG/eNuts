## Overview & Design Context
Header block for the SideBar. Inherits `SideBarItem` and composes `StatefullIcon[eSideBarState]`, `Title`, and `Description`.

* **Design Decision:** Icons dict is required (non-empty). Available asset today: `assets/icons/logo.png` (callers may use it for both Expanded and Collapsed until dedicated icons exist).

---

## Classes

### `SideBarHeader`
- **Purpose:** Top header row of the sidebar with multi-state icon and text.
- **Methods:**
  - `_wInitializeUI()` -> Builds icon + title + description into the item layout.
  - `addIcon(state, icon)` -> Registers or updates an icon for a sidebar state.
- **Properties:**
  - `Title` — header title text.
  - `Description` — header description text; hidden when empty.
  - `State` — current `eSideBarState` reflected by the statefull icon.

---

## Sample Usage

Internal to the SideBar package; constructed by `SideBar`.
