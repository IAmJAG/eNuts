# ==================================================================================
# src/jAGQt/utilities/__animation.py
# ==================================================================================
from typing import Any, Callable, Optional

# ==================================================================================
from PySide6.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QObject,
    QPropertyAnimation,
)
from PySide6.QtWidgets import QWidget


# ==================================================================================
class AnimationError(ValueError):
    """Raised when animation parameters fail validation."""


# ==================================================================================
def ValidateAnimationTarget(target: QObject, propertyName: str) -> bytes:
    """Validate that *target* exposes a Qt property named *propertyName*.

    Returns the property name encoded as bytes (required by QPropertyAnimation).
    Raises AnimationError on any validation failure.
    """
    if target is None:
        raise AnimationError("Animation target must not be None.")

    if not isinstance(target, QObject):
        raise AnimationError(
            f"Animation target must be a QObject, got {type(target).__name__}."
        )

    if not propertyName or not isinstance(propertyName, str):
        raise AnimationError("propertyName must be a non-empty string.")

    lPropName = propertyName.encode("utf-8") if isinstance(propertyName, str) else propertyName

    # Prefer the Qt meta-object check when available
    lMeta = target.metaObject()
    if lMeta is not None:
        lIndex = lMeta.indexOfProperty(propertyName)
        if lIndex < 0:
            # Fall back to Python attribute / pyqtProperty style
            if not hasattr(target, propertyName):
                raise AnimationError(
                    f"Target {type(target).__name__} has no property or attribute "
                    f"named {propertyName!r}."
                )

    return lPropName


def ValidateAnimationRange(startValue: Any, endValue: Any) -> None:
    """Basic sanity checks on the animation value range."""
    if startValue is None or endValue is None:
        raise AnimationError("startValue and endValue must not be None.")

    if startValue == endValue:
        raise AnimationError("startValue and endValue must differ for a meaningful animation.")


def CreatePropertyAnimation(
    target: QObject,
    propertyName: str,
    startValue: Any,
    endValue: Any,
    *,
    durationMs: int = 220,
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    parent: Optional[QObject] = None,
    onFinished: Optional[Callable[[], None]] = None,
) -> QPropertyAnimation:
    """Create a validated QPropertyAnimation.

    Validation is performed *before* the animation object is constructed so
    callers receive clear errors instead of silent no-ops.

    Parameters
    ----------
    target:
        Any QObject (or QWidget) that exposes the given Qt property.
    propertyName:
        Name of the Qt property to animate (e.g. "minimumWidth", "geometry",
        "windowOpacity").
    startValue / endValue:
        Values compatible with the target property type.
    durationMs:
        Duration in milliseconds. Must be >= 0.
    easing:
        QEasingCurve.Type used for the animation.
    parent:
        Optional parent for the animation object (defaults to *target*).
    onFinished:
        Optional zero-argument callback invoked when the animation finishes.

    Returns
    -------
    QPropertyAnimation
        Ready to be started with ``.start()``.
    """
    lPropName = ValidateAnimationTarget(target, propertyName)
    ValidateAnimationRange(startValue, endValue)

    if durationMs < 0:
        raise AnimationError(f"durationMs must be >= 0, got {durationMs}.")

    lParent = parent if parent is not None else target
    lAnim = QPropertyAnimation(target, lPropName, lParent)
    lAnim.setDuration(int(durationMs))
    lAnim.setEasingCurve(easing)
    lAnim.setStartValue(startValue)
    lAnim.setEndValue(endValue)

    if onFinished is not None:
        if not callable(onFinished):
            raise AnimationError("onFinished must be callable or None.")
        lAnim.finished.connect(onFinished)

    return lAnim


def AnimateProperty(
    target: QObject,
    propertyName: str,
    startValue: Any,
    endValue: Any,
    *,
    durationMs: int = 220,
    easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    parent: Optional[QObject] = None,
    onFinished: Optional[Callable[[], None]] = None,
    stopRunning: bool = True,
) -> QPropertyAnimation:
    """Validate, create, and immediately start a property animation.

    If *stopRunning* is True (default) any currently running animation on the
    same target+property is stopped before the new one begins.

    Returns the running QPropertyAnimation instance so the caller can keep a
    reference or connect additional signals.
    """
    lAnim = CreatePropertyAnimation(
        target,
        propertyName,
        startValue,
        endValue,
        durationMs=durationMs,
        easing=easing,
        parent=parent,
        onFinished=onFinished,
    )

    if stopRunning:
        # Stop any previous animation that targets the same property on this object
        for lChild in target.findChildren(QPropertyAnimation):
            if (
                lChild.targetObject() is target
                and lChild.propertyName() == lAnim.propertyName()
                and lChild.state() == QAbstractAnimation.State.Running
            ):
                lChild.stop()

    lAnim.start()
    return lAnim
