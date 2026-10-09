# SideBar

**Package:** `jAGQt.widgets.sideBar`  
**Source:** `src/jAGQt/widgets/SideBar/`

## Overview

`SideBar` is a dockable, collapsible navigation panel for PySide6 applications.

It composes reusable leaf widgets (header, items, groups, dock control) and orchestrates:

- **Left / right docking** with a bottom arrow control
- **Collapse / expand** with rubber-band width animation
- **Nested groups** (no chevrons — header click toggles body)
- **Selection cascade** (one active leaf; ancestor headers selected)
- **Theme-driven styling** via dynamic QSS properties only (no font weight/size in code)
- **Dock transfer animation** (lightning ball → tentacle → rematerialize)

Conceptually:

    SideBar
    ├── SideBarHeader          (burger / X morph, title)
    ├── SideBarContent         (scroll area)
    │   ├── SideBarItem        (leaf, depth N)
    │   ├── SideBarGroup       (header + rollable body)
    │   │   ├── SideBarItem
    │   │   └── SideBarGroup   (nested, depth N+1)
    │   └── SideBarSeparator
    └── SideBarDockControl     (edge arrow, transpose on flip)

## Design rules

| Rule | Detail |
|------|--------|
| No chevrons | Group expand/collapse is the header `SideBarItem` itself |
| Depth only in code | Code sets `depth`, `role`, `active`, `selected` — never font weight or point size |
| Child icons smaller | Nested items use parent `iconSize - 2` |
| Ancestor selection | Active leaf ⇒ every ancestor header gets `selected` (dimmer via QSS by depth) |
| QSS owns look | Ironman (and other themes) style object names + dynamic properties |

## Configuration (`sideBarConfig`)

Located in `__options.py`.

| Option | Default | Description |
|--------|--------:|-------------|
| `expandedWidth` | 240 | Width when expanded |
| `collapsedWidth` | 48 | Width when collapsed (icon strip) |
| `iconSize` | derived | Square icon size (`collapsedWidth - padding`) |
| `dockPosition` | `DockPosition.Left` | Initial dock side |
| `startCollapsed` | `False` | Initial collapsed state |
| `animationDuration` | 220 | Base duration (ms) for related animations |

Example:

    from jAGQt.widgets.sideBar import SideBar
    from jAGQt.widgets.sideBar.__options import sideBarConfig
    from jAGQt.types import DockPosition

    cfg = sideBarConfig()
    # or pass kwargs that map to _fields if extended

    bar = SideBar(title="eNuts", config=cfg)

## Public API — `SideBar`

### Construction

    SideBar(title="", config=None, parent=None)

### Content

| Method | Description |
|--------|-------------|
| `AddItem(text, icon=None, …)` | Root-level leaf item (`depth=0`, `role=leaf`) |
| `AddGroup(title, icon=None, startCollapsed=False)` | Root group; returns `SideBarGroup` |
| `AddSeparator()` | Horizontal separator |
| `AddStretch()` | Flexible spacer in content |
| `Clear()` | Remove all content and selection |

Nested content is built on the group:

    devices = bar.AddGroup("Devices")
    devices.AddItem("Emulator")
    remote = devices.AddGroup("Remote", startCollapsed=True)
    remote.AddItem("SSH Bridge")

### Collapse

| API | Description |
|-----|-------------|
| `SetCollapsed(bool)` / `Collapsed` | Animate width (rubber-band) |
| `ToggleCollapse()` | Invert collapsed state |
| Header burger/X | Emits `CollapseRequested`; SideBar toggles |

Collapsed mode switches items/groups to icon-only display and forces nested groups closed.

### Dock

| API | Description |
|-----|-------------|
| `SetDockSide(DockPosition, animate=True)` | Left ↔ right |
| `ToggleDockSide()` | Flip side |
| Bottom arrow | Emits flip; triggers lightning transfer when animated |

Animated dock sequence:

1. SideBar hides; silhouette collapses into a **lightning ball**
2. **Tentacle** shoots from the ball to the opposite edge
3. At midpoint, layout reparents the bar to the destination side
4. Ball **rematerializes** into a panel silhouette; SideBar is shown again

### Selection

| API | Description |
|-----|-------------|
| `SelectItem(SideBarItem)` | Programmatic selection |
| Item / group clicks | Emit `ItemClicked`; cascade applied automatically |

Cascade behavior:

- Exactly one item has `active="true"`
- Ancestor group headers under that item receive `selected="true"`
- QSS dims selected ancestors by `depth`

### Persistence helpers

| API | Description |
|-----|-------------|
| `ExportState()` | `{"collapsed": bool, "dockSide": "left"\|"right"}` |
| `RestoreState(collapsed, dockSide)` | Apply without animation |

The application shell is expected to store these values (e.g. `QSettings`). Boolean restore must parse string/`0`/`1` values carefully — never use bare `bool("false")`.

### Signals

| Signal | Payload |
|--------|---------|
| `CollapseRequested` | — |
| `CollapsedChanged` | `bool` |
| `DockSideChanged` | `DockPosition` |
| `ItemClicked` | `SideBarItem` |

## Components

### `SideBarHeader`

- Layout: `[toggle icon] [title]`
- Expanded: burger + title
- Collapsed: close (X), title hidden
- Icon size is a single square int
- Burger ↔ X uses `IconMorphAnimation`

Object names: `SideBarHeader`, `SideBarHeaderToggle`, `SideBarHeaderTitle`

### `SideBarItem`

Unified row for leaves and group headers.

Dynamic properties set by code:

| Property | Values |
|----------|--------|
| `depth` | `"0"`, `"1"`, `"2"`, … |
| `role` | `"leaf"` / `"header"` |
| `active` | `"true"` / `"false"` |
| `selected` | `"true"` / `"false"` |
| `hover` | `"true"` / `"false"` |

Object names: `SideBarItem`, labels `SideBarText` / `SideBarIcon`

### `SideBarGroup`

- Header is a `SideBarItem` with `role=header` (object name `SideBarGroupHeader`)
- Body rolls open/closed via `RollAnimation` (`maximumHeight`)
- `AddItem` / `AddGroup` / `AddSeparator` / `Clear`
- `CollectItems()` / `FindAncestorHeaders(item)` support selection cascade
- `SetSidebarCollapsed(bool)` syncs icon-only mode when the bar collapses

### `SideBarDockControl`

- Dock left → right-pointing arrow at bottom-right
- Dock right → left-pointing arrow at bottom-left
- Arrow swap uses `IconTransposeAnimation`

### `SideBarContent`

Scroll area hosting root widgets; vertical only.

### Leaf helpers

- `SideBarIcon` — square pixmap/icon host
- `SideBarText` — label (typography from QSS)
- `SideBarSeparator` — line or spacer style

## Animations used

| Animation | Package | Role in SideBar |
|-----------|---------|-----------------|
| `RubberBandAnimation` | `jAGQt.animations` | Collapse / expand width (overshoot → undershoot → settle via `setFixedWidth`) |
| `RollAnimation` | `jAGQt.animations` | Group body open / close |
| `LightningShootAnimation` | `jAGQt.animations` | Dock transfer (ball → tentacle → rematerialize) |
| `IconMorphAnimation` | `jAGQt.icons.animations` | Header burger ↔ X |
| `IconTransposeAnimation` | `jAGQt.icons.animations` | Dock arrow flip |

## Theme / QSS

Styling lives in theme CSS (e.g. `config/eNuts/ironman.css`), not in Python.

Important selectors:

- `QWidget#SideBar`, `#SideBarHeader`, `#SideBarContent`, `#SideBarDockControl`
- `QWidget#SideBarItem`, `#SideBarGroupHeader` with `[depth]`, `[active]`, `[selected]`, `[role]`
- `QLabel#SideBarText`, `#SideBarGroupTitle`, `#SideBarHeaderTitle` — **set color explicitly** (Qt does not reliably honor `color: inherit`)

Dynamic properties on the root bar:

- `collapsed` = `"true"` / `"false"`
- `dockSide` = `"left"` / `"right"`

## Integration sketch (Shell)

    bar = SideBar(title="eNuts")
    bar.DockSideChanged.connect(onDockChanged)
    bar.CollapsedChanged.connect(onCollapsedChanged)

    bar.AddItem("Home")
    g = bar.AddGroup("Devices")
    g.AddItem("Emulator")

    # restore from QSettings (safe bool parse)
    bar.RestoreState(collapsed, dockSide)

    layout.insertWidget(0, bar)  # or addWidget for right dock

On `DockSideChanged`, remove the bar from the shell layout and re-insert at index 0 (left) or append (right).

## File map

    src/jAGQt/widgets/SideBar/
    ├── __init__.py
    ├── __sideBar.py          # SideBar orchestrator
    ├── __options.py          # sideBarConfig
    └── components/
        ├── __sideBarHeader.py
        ├── __sideBarContent.py
        ├── __sideBarItem.py
        ├── __sideBarGroup.py
        ├── __dockControl.py
        ├── __sideBarIcon.py
        ├── __sideBarText.py
        ├── __sideBarSeparator.py
        └── __sideBarIcons.py   # re-exports of shared icon makers

Related packages:

- `src/jAGQt/animations/` — drawer, rubber-band, roll, lightning
- `src/jAGQt/icons/` — code-drawn icons + morph/transpose
- `config/eNuts/ironman.css` — SideBar theme rules

## Summary

`SideBar` is a **composition-first** navigation chrome:

- Build structure with `AddItem` / `AddGroup`
- Drive look with theme QSS properties
- Collapse with rubber-band width
- Dock with lightning transfer
- Persist collapsed + dock side through `ExportState` / `RestoreState`
