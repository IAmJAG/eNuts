# Implementation Details

## 1. Architecture Overview
UI widgets under `src/eNuts/UI/widgets/` are page-facing surfaces (spinners, etc.). Stream hosts are `jAGQt.widgets.Canvas` / `GLCanvas`. Input is forwarded via Qt signals; application controllers inject/log.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/widgets/Canvas/__canvas.py` | (jAGQt Canvas) | Software canvas + input signals |
| `src/jAGQt/widgets/Canvas/__glCanvas.py` | (jAGQt Canvas) | OpenGL canvas + input signals + `present` |
| `src/eNuts/UI/widgets/spinners/` | (spinners) | Loading spinners |

## 3. Core Workflows & Data Flow
1. Page constructs `GLCanvas` (or `Canvas`) as `_streamView`.
2. Page wires key/mouse signals to inject/log slots.
3. Presenter (or transitional stream path) calls `present` / sets `image` independently of input.
