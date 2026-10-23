# Component & UI Issues

### 1. Icon Animation Refactor (`StatefulIcon`)

* **Objective:** Decouple animation management from `StatefulIcon` to improve separation of concerns and component flexibility.
* **Requirements:**
  * Remove internal animation-building responsibilities from `StatefulIcon`.
  * Enable the component to optionally accept animation configuration options.
  * Construct the animation internally using the provided options.
  * Restrict `StatefulIcon`'s interaction with the animation strictly to triggering its start and end states.
* **Status:** Open

---

### 2. Sidebar Menu: Ghost / Stale Leaf under Devices

* **Issue Description:** A persistent extra leaf under **Devices** (often the initial `(no devices)` placeholder) remained visible after real devices were discovered, or left a "ghost" row until the sidebar was collapsed/expanded.
* **Root Cause Analysis:**
  1. **Placeholder design:** Menu was built with a static `(no devices)` child at init. Discovery is async, so the leaf existed before any real device.
  2. **Incomplete teardown:** `clearChildren()` only `setParent(None)` without `deleteLater()`, so Qt could keep a detached widget until a layout/state pass (e.g. SideBar collapse/expand) forced a repaint/relayout — matching "disappears after state change".
  3. **deviceManager store (earlier):** Subclassing `Dict` without a reliable internal map could make `values()` empty on first UI sync, so rebuild kept or re-added the placeholder.
* **Resolution (2026-10-18):**
  * Do **not** create a `(no devices)` leaf at all — Devices header only until discovery adds real leaves.
  * `clearChildren()` now hides, unparents, and `deleteLater()`s each child.
  * `deviceManager` uses an explicit `_devices` dict.
* **Status:** Mitigated — re-verify on load with 0 devices then with N devices; confirm no ghost after discovery without toggling the rail.
* **Follow-up:** If a ghost still appears, inspect SideBarMenu body reparent (`attachBodyTo` / column layout) for a second reference to the old child widget.

---

### 3. Logging: Unicode arrow on Windows (cp1252)

* **Issue Description:** `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'` when logging messages that used `→`.
* **Root Cause:** Windows console / rotating file handler using **cp1252** cannot encode U+2192.
* **Resolution:** Use ASCII `->` in log strings (WorkSpace device menu messages).
* **Status:** Fixed for known call sites. Prefer ASCII in all `verbose`/`error` messages going forward.

---

### 4. `newLayout` + `QVBoxLayout` / `QHBoxLayout`

* **Issue Description:** `TypeError` when `newLayout(QVBoxLayout, ...)` passed `Direction` into the constructor.
* **Root Cause:** Only `QBoxLayout` accepts `Direction` in `__init__`; `QVBoxLayout`/`QHBoxLayout` do not.
* **Resolution:** Prefer `QBoxLayout` + direction; `newLayout` hardened for V/H box types.
* **Status:** Fixed (Header + utility).

---

### 5. SCRCPY / device page stream (planned)

* **Notes for Phase 5+:** `SCRCPYEmitter` raises `ON_FRAME` with `iFrame`; UI should marshal frames to the Qt thread and push into `jAGQt.widgets.Image` (`image` accepts `QPixmap` / `QImage` / path / Tensor). Open until device page content is wired.
* **Status:** Open (design only).


# Descrete-Continues Policy 
* ** TODO: GPU Tensor path - path for purely originated from GPU