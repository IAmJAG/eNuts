# Requirements & Design Specifications

## 1. Project Overview
SideBar provides a fixed-width vertical navigation chrome with a multi-state header icon and optional title/description. Expand/collapse behavior is prepared via `eSideBarState` but not fully wired yet.

## 2. Functional Requirements
- **FR-1:** SideBar hosts a header item at the top and a stretch below (no content widget).
- **FR-2:** Header uses `StatefullIcon` keyed by `eSideBarState`, plus `Title` and `Description` from the text package.
- **FR-3:** Icons mapping is required and non-empty at construction.
- **FR-4:** Package public API exposes only `SideBar` and `eSideBarState`.
- **FR-5:** `SideBarItem` and `SideBarHeader` live under `SideBar.components` and are internal.

## 3. Non-Functional Requirements
- **NFR-1:** Follow ComponentBase / ObjectName / `@workflow` patterns used elsewhere in jAGQt widgets.
- **NFR-2:** Documentation mirrors source under `.docs/jAGQt/widgets/sideBar/`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Required icons with single available asset
- **Affected Modules:** `SideBar/__sideBar.py`, `SideBar/components/__sideBarHeader.py`
- **Description of Standard / Best Practice:** Often provide default icons for empty construction.
- **Divergence:** Icons dict is mandatory; no built-in defaults.
- **Design Decision & Justification:** Caller owns branding; only `assets/icons/logo.png` exists today and may be reused per state until expand/collapse assets are added.
- **Code Doc Cross-Reference:** See `sideBar.md` and `components/sideBarHeader.md`.
