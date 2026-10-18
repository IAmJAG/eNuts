## Overview & Design Context
Base row widget for SideBar chrome. Provides a horizontal layout with a leading slot and a vertical text column. `SideBarHeader` specializes this item.

---

## Classes

### `SideBarItem`
- **Purpose:** Shared layout shell for sidebar rows (header now; other rows later).
- **Methods:**
  - `_wInitializeUI()` -> Builds horizontal layout and text column.
  - `_addLeading(widget)` -> Inserts a leading widget at the start of the row.
  - `_addTextWidget(widget)` -> Appends a widget to the text column.

---

## Sample Usage

Internal to the SideBar package only; not exported from `jAGQt.widgets.SideBar`.
