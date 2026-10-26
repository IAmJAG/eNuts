# Implementation Details

## 1. Architecture Overview
Page is a `QWidget` + `ComponentBase` that builds three vertical regions:
1. Header
2. Content (owned layout targeted by `Page.Layout`)
3. Optional CommandBar

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/page/__page.py` | `.docs/jAGQt/widgets/page/page.md` | Page widget |
| `src/jAGQt/widgets/header/__header.py` | `.docs/jAGQt/widgets/header/header.md` | Header used by Page |

## 3. Core Workflows & Data Flow
- Construction stores title/description/icon until `_wInitializeUI`.
- `_wInitializeUI` creates Header with those three values, then builds content + optional command bar.
- Property setters for Title / Description / Icon / IconPosition forward to the live Header instance and trigger layout rebuild when needed.
