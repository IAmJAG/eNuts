# Requirements & Design Specifications

## 1. Project Overview
Navigation owns page-id constants, the static menu/page table (`PAGE_AND_MENU`), blank/specialised page builders, and the dynamic SideBar menu walker.

## 2. Functional Requirements
- **FR-1:** Every static menu entry and page is identified only by an existing page-id constant (no invented caption keys).
- **FR-2:** `PAGE_AND_MENU` is the single table for static menu structure and page metadata (title, description, icon).
- **FR-3:** `buildSideBarMenu` walks a structure (default `PAGE_AND_MENU`); it does not hard-code captions or keys.
- **FR-4:** `buildNavigationPages` walks the same table; specialised pages via `_PAGE_BUILDERS`; `Page.Id` equals the page id.
- **FR-5:** Device pages remain dynamic in `WorkSpace` and are not listed in `PAGE_AND_MENU`.

## 3. Non-Functional Requirements
- **NFR-1:** Adding a static page requires only a page-id constant (if new) + one `PAGE_AND_MENU` entry + optional builder registration.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Page keys moved from `pages` to `navigation`
- **Affected Modules:** `src/eNuts/UI/navigation/__pageKeys.py`, `src/eNuts/UI/pages/__pageKeys.py` (shim)
- **Description of Standard / Best Practice:** Keys colocated with the feature that defines navigation structure.
- **Divergence:** `pages/__pageKeys.py` remains a re-export shim for older imports.
- **Design Decision & Justification:** Navigation is the owner of menu + page registry identity; pages package only implements page bodies.
- **Code Doc Cross-Reference:** See `pageKeys.md`, `navigation.md`, `sideBarMenuBuilder.md`.
