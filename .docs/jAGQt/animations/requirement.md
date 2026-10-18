# Requirements & Design Specifications

## 1. Project Overview
Provide a reusable base for custom Qt animations (beyond one-off `QPropertyAnimation` helpers in utilities).

## 2. Functional Requirements
- **FR-1:** Base class exposes `start`, `stop`, `isRunning`, `durationMs`.
- **FR-2:** Subclasses receive normalized progress in `[0.0, 1.0]` via `_onProgress`.
- **FR-3:** Failures during start/stop/progress are logged and re-raised (not swallowed).
- **FR-4:** Protocol `iAnimation` documents the public contract.

## 3. Non-Functional Requirements
- **NFR-1:** Align with existing `jAGQt.utilities` animation validation helpers where useful.
- **NFR-2:** Documentation under `.docs/jAGQt/animations/`.

## 4. Design Decisions & Standards Deviations

### Issue / Item 1: ABC + QObject
- **Affected Modules:** `animations/__animationBase.py`
- **Description of Standard / Best Practice:** Prefer either pure Protocol or pure QObject hierarchies.
- **Divergence:** `AnimationBase` is `QObject` + `ABC` so subclasses must implement `_onProgress` while remaining a Qt object with signals.
- **Design Decision & Justification:** Custom frame animations need signals and a timer/driver; abstract method enforces the extension point.
- **Code Doc Cross-Reference:** See `animationBase.md`.
