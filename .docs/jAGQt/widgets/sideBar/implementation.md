# Implementation Details

## 1. Architecture Overview
```text
SideBar
├── SideBarHeader (components) — StatefullIcon drives eSideBarState
├── Content host (stretch)
│   └── optional content QWidget
└── optional iAnimation (from SideBarOptions.animation class name)

Options apply → properties → drop
toOptions() ← properties
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/SideBar/__sideBar.py` | `.docs/jAGQt/widgets/sideBar/sideBar.md` | Host layout, options, width |
| `src/jAGQt/widgets/SideBar/__eSideBarState.py` | `.docs/jAGQt/widgets/sideBar/eSideBarState.md` | State enum |
| `src/jAGQt/widgets/SideBar/components/__sideBarItem.py` | `.docs/jAGQt/widgets/sideBar/components/sideBarItem.md` | Row base |
| `src/jAGQt/widgets/SideBar/components/__sideBarHeader.py` | `.docs/jAGQt/widgets/sideBar/components/sideBarHeader.md` | Header row |
| `src/jAGQt/options/*` | `.docs/jAGQt/options/` | Options types |

## 3. Core Workflows & Data Flow
1. Ctor stores icons/title/description/options until `_wInitializeUI`.
2. Build header + content host layout.
3. `_applyOptions` copies widths; `_resolveAnimation` builds instance or None.
4. `stateChanged` → target width from properties; `animation.start(endWidth=…)` or `setFixedWidth`.
5. On animation finished/stopped: snap width and chrome.
6. `toOptions()` exports widths + animation class name string.

## 4. Assets / theme samples
- `config/themes/dark/options/SideBar.json`
- `config/themes/dark/options/Animation.json`
