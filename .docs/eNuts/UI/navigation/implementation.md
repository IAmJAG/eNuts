# Implementation Details

## 1. Architecture Overview
- `__pageKeys.py` — constants + device key helpers
- `__navigation.py` — `PAGE_AND_MENU`, `buildBlankPage`, `buildNavigationPages`
- `__sideBarMenuBuilder.py` — `setPageKey` / `pageKeyOf` / `buildSideBarMenu`
- `__init__.py` — public re-exports

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/eNuts/UI/navigation/__pageKeys.py` | `.docs/eNuts/UI/navigation/pageKeys.md` | Page ids + device keys |
| `src/eNuts/UI/navigation/__navigation.py` | `.docs/eNuts/UI/navigation/navigation.md` | PAGE_AND_MENU + page registry |
| `src/eNuts/UI/navigation/__sideBarMenuBuilder.py` | `.docs/eNuts/UI/navigation/sideBarMenuBuilder.md` | Dynamic menu from structure |

## 3. Core Workflows & Data Flow
1. `WorkSpace._wBuildMenu` calls `buildSideBarMenu()` → walks `PAGE_AND_MENU` → sets `pageKey` on each item.
2. `buildNavigationPages()` walks the same table → returns `{pageId: Page}` with `Page.Id == pageId`.
3. Click handler uses `pageKeyOf(item)` → `WorkSpace.showPage(key)`.
