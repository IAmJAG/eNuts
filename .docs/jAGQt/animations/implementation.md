# Implementation Details

## 1. Architecture Overview
```text
iAnimation (Protocol)
    ^ (structural)
AnimationBase (QObject + ABC)
    └── QVariantAnimation driver (0.0 → 1.0)
            └── _onProgress(progress)  # subclass
```

Property helpers remain in `jAGQt.utilities.__animation` (`CreatePropertyAnimation`, `AnimateProperty`). Custom/non-property animations inherit `AnimationBase`.

## 2. Directory & Module Mapping
| Source Path | Documentation Path | Primary Responsibility |
| :--- | :--- | :--- |
| `src/jAGQt/animations/__animationBase.py` | `.docs/jAGQt/animations/animationBase.md` | Base lifecycle + progress |
| `src/jAGQt/types/interface/animations/__animation.py` | (contract) | `iAnimation` Protocol |

## 3. Core Workflows & Data Flow
1. Subclass implements `_onProgress`.
2. `start()` resets driver, calls `_onStart`, starts `QVariantAnimation`.
3. Each value change → `_onProgress(float)`.
4. Full completion → `_onProgress(1.0)`, `_onFinished`, `finished` signal.
5. `stop()` stops driver, `_onStop`, `stopped` signal.

## 4. Next steps (not in this change)
- `IconMorphAnimation(AnimationBase)` under icon/animations.
- Wire into `StatefullIcon` state transitions.
