## Overview & Design Context
Builds `SideBarMenu` content and footer by walking a structure (default `PAGE_AND_MENU`). No hard-coded captions or page ids inside the builder.

---

## Functions

### `setPageKey` / `pageKeyOf`
- **Behavior:** Attach / read property `pageKey` on `SideBarMenuItem`.

### `buildSideBarMenu`
- **Arguments:** `structure` optional; defaults to `PAGE_AND_MENU`
- **Returns:** `(SideBarMenu, Optional[SideBarMenuItem])` — content menu and last footer item
- **Behavior:** Headers for top-level CONTENT entries; nested `MENU` as children (`Leaf`); FOOTER as standalone header item(s) with `selectionRequested` wired when present.

## Sample Usage

```python
from eNuts.UI.navigation import buildSideBarMenu, pageKeyOf

menu, footer = buildSideBarMenu()
# inject alternate structure in tests:
menu2, _ = buildSideBarMenu({"CONTENT": {}, "FOOTER": {}})
```
