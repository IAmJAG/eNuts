# Icons

**Package:** `jAGQt.icons`  
**Source:** `src/jAGQt/icons/`

## Overview

Code-drawn square icons and icon animations for jAGQt widgets (SideBar header toggle, dock arrows, etc.).

Icon size is always a **single integer** (square). There is no separate width/height API.

## Icon makers

Typical exports (via `jAGQt.icons`):

| Factory | Use |
|---------|-----|
| `MakeBurgerIcon(size)` | Expanded SideBar header |
| `MakeCloseIcon(size)` | Collapsed SideBar header |
| `MakeArrowLeftIcon(size)` | Dock-right control |
| `MakeArrowRightIcon(size)` | Dock-left control |

Each returns a `QIcon` painted for the given pixel size.

## Icon animations

**Package:** `jAGQt.icons.animations`

### `IconMorphAnimation`

Cross-fade / morph between two icons on a target icon widget (e.g. burger ↔ X).

### `IconTransposeAnimation`

Flip-style transition when swapping direction glyphs (e.g. dock arrows).

## Design notes

- SideBar never hard-codes icon bitmaps beyond these factories
- Theme colors for chrome come from QSS; icon stroke colors are chosen for dark Ironman contrast
- Prefer regenerating icons when `iconSize` changes rather than scaling bitmaps up

## Summary

Use **makers** for static glyphs and **morph/transpose** when the glyph itself must animate between two states.
