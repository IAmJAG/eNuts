# Implementation Details

## 1. Architecture Overview
```text
SideBar
├── SideBarHeader (components)
│   └── SideBarItem
│       ├── StatefullIcon[eSideBarState]
│       └── Title / Description
└── stretch (1)

eSideBarState  (package root, public)
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/SideBar/__sideBar.py` | `.docs/jAGQt/widgets/sideBar/sideBar.md` | Host layout |
| `src/jAGQt/widgets/SideBar/__eSideBarState.py` | `.docs/jAGQt/widgets/sideBar/eSideBarState.md` | State enum |
| `src/jAGQt/widgets/SideBar/components/__sideBarItem.py` | `.docs/jAGQt/widgets/sideBar/components/sideBarItem.md` | Row base |
| `src/jAGQt/widgets/SideBar/components/__sideBarHeader.py` | `.docs/jAGQt/widgets/sideBar/components/sideBarHeader.md` | Header row |

## 3. Core Workflows & Data Flow
1. Caller constructs `SideBar(icons={...}, title=..., description=...)`.
2. `_wInitializeUI` builds `SideBarHeader` and a vertical layout with stretch.
3. Header builds `StatefullIcon` from the icons dict, then `Title` / `Description`.
4. Setting `SideBar.State` updates the statefull icon for future expand/collapse UX.

## 4. Assets
- Current icon asset under repo: `assets/icons/logo.png` only.
