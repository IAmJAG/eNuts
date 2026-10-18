# Requirements & Design Specifications

## 1. Project Overview
Named, serializable configuration settings for jAGQt widgets and animations. Options are applied once to a host (copy onto host properties) then dropped. Persistence lives under theme directories via `getConfigPath`.

## 2. Functional Requirements
- **FR-1:** `OptionsBase` provides `Name`, `Version`, `Description`, and `resolvePath(themeName)`.
- **FR-2:** `SideBarOptions` adds `expandedWidth`, `collapsedWidth`, and `animation` (class name string or empty).
- **FR-3:** `AnimationOptions` adds `durationMs`.
- **FR-4:** Both concrete types inherit `OptionsBase` and `Serializable` encode/decode.
- **FR-5:** Path shape: `config/themes/<theme>/options/<Name>.json` via `getConfigPath`.
- **FR-6:** Options are settings only — not long-lived tracked objects on the host after apply.

## 3. Non-Functional Requirements
- **NFR-1:** Follow project naming conventions and `Serializable` property list pattern (`ApplicationConfiguration`).
- **NFR-2:** Documentation under `.docs/jAGQt/options/`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: Animation field is a class name, not an instance
- **Affected Modules:** `SideBarOptions`, `SideBar`
- **Description of Standard / Best Practice:** Config often embeds full nested objects.
- **Divergence:** Disk options store a fully qualified class name; the host resolves and constructs the live `iAnimation`.
- **Design Decision & Justification:** Live `QObject` animations are not JSON-safe; factory/apply owns construction with `target=host`.
- **Code Doc Cross-Reference:** `sideBarOptions.md`, SideBar `implementation.md`.

### Issue / Item 2: Save I/O not on OptionsBase
- **Affected Modules:** `OptionsBase`
- **Description of Standard / Best Practice:** Some config types own `load`/`save`.
- **Divergence:** Theme handler (or caller) performs I/O; options only `encode`/`decode`/`resolvePath`.
- **Design Decision & Justification:** Matches “saving is the theme handler” and keeps options as pure settings.
