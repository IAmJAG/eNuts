## Overview & Design Context
`PAGE_AND_MENU` describes static SideBar content/footer and supplies title/description/icon for page construction. Keys are page ids from `__pageKeys.py` only.

---

## Constants & Globals

### `PAGE_AND_MENU`
- **Type:** `Dict[str, Dict[str, Any]]`
- **Value / Description:** Sections `CONTENT` / `FOOTER`. Nested `MENU` under a header is also keyed by page id.

### `_PAGE_BUILDERS`
- **Type:** `Dict[str, Callable[[str], Page]]`
- **Description:** Specialised builders (e.g. `PAGE_KG_RECORDER` → `buildKGRecorderPage`).

---

## Functions

### `buildBlankPage`
- **Arguments:** `key` (str), `title` (str), `description` (str)
- **Returns:** `Page` with `Id == key`

### `buildNavigationPages`
- **Arguments:** none
- **Returns:** `dict[str, Page]`
- **Behavior:** Flattens `PAGE_AND_MENU`; uses `_PAGE_BUILDERS` or `buildBlankPage`; always registers `PAGE_DEVICES` for stack lookup.

## Sample Usage

```python
from eNuts.UI.navigation import PAGE_AND_MENU, buildNavigationPages

pages = buildNavigationPages()
assert pages["kg-recorder"].Id == "kg-recorder"
```
