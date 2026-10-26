# Implementation Details

## 1. Architecture Overview
Header owns three child widgets: `Title`, `Description`, and `Icon`. `_rebuildLayout` clears the outer `QBoxLayout` and re-parents children according to `IconPosition`.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/header/__header.py` | `.docs/jAGQt/widgets/header/header.md` | Header widget |
| `src/jAGQt/widgets/header/__iconPosition.py` | (enum) | Placement enum |

## 3. Core Workflows & Data Flow
- Defaults for position/size/BG/FG are set in `__init__` and survive `_wInitializeUI`.
- Property setters update the corresponding private field (and the `Icon` child when colors change) then call `_rebuildLayout`.
- `hasIcon` now also checks that the Icon actually has content so empty icons do not reserve space.
