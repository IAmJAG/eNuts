# Implementation Details

## 1. Architecture Overview
```text
OptionsBase (Serializable)
├── SideBarOptions   (widths + animation class name)
└── AnimationOptions (durationMs)

Theme path: getConfigPath("themes/<name>/options/<Name>.json")
```

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/options/__optionsBase.py` | `.docs/jAGQt/options/optionsBase.md` | Named options base |
| `src/jAGQt/options/__sideBarOptions.py` | `.docs/jAGQt/options/sideBarOptions.md` | SideBar settings |
| `src/jAGQt/options/__animationOptions.py` | `.docs/jAGQt/options/animationOptions.md` | Animation settings |

## 3. Core Workflows & Data Flow
1. Construct or `decode` options from JSON.
2. Pass into host (`SideBar(..., options=..., animationOptions=...)`).
3. Host copies fields to instance properties and resolves animation class name.
4. Options references are dropped.
5. Host `toOptions()` rebuilds a settings blob from properties for external save.
