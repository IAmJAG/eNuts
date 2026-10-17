## Overview & Design Context
Fixed-width sidebar host with header, content slot, and optional width animation from options.

* **Design Decision:** Public package surface remains `SideBar` and `eSideBarState`. Options apply-then-drop. Animation is start/stop only on the host.

---

## Classes

### `SideBar`
- **Purpose:** Application sidebar shell.
- **Methods:**
  - `_wInitializeUI()` -> Header, content host, apply options, wire state.
  - `_applyOptions(options, animationOptions)` -> Copy settings to properties; resolve animation.
  - `_resolveAnimation(className, animationOptions)` -> `iAnimation` or None.
  - `toOptions()` -> `SideBarOptions` from current properties.
  - `setContent(widget)` -> Place/replace content below header.
  - `_syncLayoutForState(state, animate=…)` -> Width + chrome.
- **Properties:**
  - `Header`, `Content`, `Title`, `Description`
  - `ExpandedWidth`, `CollapsedWidth`, `Animation`, `State`

---

## Sample Usage

```python
from jAGQt.widgets.SideBar import SideBar, eSideBarState
from jAGQt.options import SideBarOptions, AnimationOptions

sidebar = SideBar(
    icons={
        eSideBarState.Expanded: "assets/icons/expand.png",
        eSideBarState.Collapsed: "assets/icons/collapse.png",
    },
    title="eNuts",
    options=SideBarOptions(animation="jAGQt.animations.RubberBand"),
    animationOptions=AnimationOptions(durationMs=280),
)
sidebar.State = eSideBarState.Collapsed
exported = sidebar.toOptions()
```
