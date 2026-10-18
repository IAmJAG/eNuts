# Requirements & Design Specifications

## 1. Project Overview
Base SideBar chrome: header, content slot, expand/collapse width driven by header `StatefullIcon` state. Optional width animation resolved from options class name. No menu or selection.

## 2. Functional Requirements
- **FR-1:** Host header + content region; public API `SideBar`, `eSideBarState`.
- **FR-2:** Accept optional `SideBarOptions` / `AnimationOptions`; apply to properties then drop.
- **FR-3:** `toOptions()` re-populates `SideBarOptions` from current properties.
- **FR-4:** Animate width only when a runtime animation instance is present; otherwise instant width.
- **FR-5:** SideBar only starts/stops animation and may react to finished/stopped.
- **FR-6:** Validate state against registered header icon keys before set.
- **FR-7:** Icons dict required and non-empty; Description is header-only.
- **FR-8:** `SideBarItem` remains a layout shell only (unchanged contract).

## 3. Non-Functional Requirements
- **NFR-1:** ComponentBase / ObjectName / `@workflow` patterns.
- **NFR-2:** Docs under `.docs/jAGQt/widgets/sideBar/`.
- **NFR-3:** QSS targets `OBJECT_NAME` values (`W_SIDEBAR`, etc.).

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Options apply-then-drop
- **Affected Modules:** `SideBar/__sideBar.py`
- **Divergence:** No long-lived options object on the widget.
- **Design Decision & Justification:** Properties are LC source of truth; options are settings.

### Issue / Item 2: Animation class name on options
- **Affected Modules:** `SideBarOptions`, `SideBar`
- **Divergence:** Resolve via `importClass` at apply; construct with `target=self`.
- **Design Decision & Justification:** Serializable config without embedding QObjects.
