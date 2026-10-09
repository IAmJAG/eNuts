# Animations

**Package:** `jAGQt.animations`  
**Source:** `src/jAGQt/animations/`

## Overview

Reusable widget animations used across jAGQt (notably SideBar).

All concrete animations subclass `AnimationBase`:

- `Start()` / `Stop()`
- `Finished` signal
- Configurable duration and easing

## Classes

### `AnimationBase`

Abstract base. Subclasses implement `_onStart` / `_onStop` and call `_emitFinished()` when done.

### `DrawerAnimation`

Smooth width change via `setFixedWidth` each frame (`QVariantAnimation`).  
Use for simple panel open/close without overshoot.

### `RubberBandAnimation`

Width rubber-band with keyframes:

1. Move past target (**overshoot**)
2. Snap slightly back (**undershoot**)
3. Settle on final width

Important: drives **real width** with `setMinimumWidth` / `setMaximumWidth` / `setFixedWidth`. Animating only `maximumWidth` does nothing useful when the widget is fixed-width locked.

    anim.SetRange(startWidth, endWidth, overshootPx=28, undershootPx=10)
    anim.Start()

### `RollAnimation`

Vertical roll via `maximumHeight` (group bodies, drawers that grow downward).

    anim.SetRange(startHeight, endHeight)
    anim.Start()

Helpers: `RollDown(endHeight)`, `RollUp()`.

### `LightningShootAnimation`

Three-phase transfer effect:

| Phase | Progress | Visual |
|-------|----------|--------|
| Form ball | 0–22% | Source silhouette collapses into a plasma/lightning ball |
| Tentacle | 22–72% | Jagged bolt grows from ball to destination |
| Rematerialize | 72–100% | Ball reforms at dest and expands into a panel silhouette |

API:

    anim.SetPathPoints(
        host,
        start=QPointF(...),
        end=QPointF(...),
        sourceSize=QPointF(w, h),
        destSize=QPointF(w, h),
        hideSource=True,
        onMidpoint=callback,  # layout flip while still hidden
    )
    anim.Start()

Signals: `Midpoint` (tentacle arrived), `Finished`.

When `hideSource` is true, the source widget is hidden for the duration and shown again on cleanup.

## File map

    src/jAGQt/animations/
    ├── __init__.py
    ├── __base.py
    ├── __drawer.py
    ├── __rubberBand.py
    ├── __roll.py
    └── __lightning.py

## Summary

Prefer **RubberBand** for SideBar width, **Roll** for nested section height, **Lightning** for dramatic cross-window widget transfer.
