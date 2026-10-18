# ==================================================================================
# src/jAGQt/animations/blinds/__blindsAnimationBase.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from ..__sizeAnimationBase import SizeAnimationBase
from .__eBlindsOrientation import eBlindsOrientation

# ==================================================================================
C_DEFAULT_STRIPS = 8
# ==================================================================================


# ==================================================================================
class BlindsAnimationBase(SizeAnimationBase):
    """Size animation that advances in discrete strip steps (blinds)."""

    def __init__(
        self,
        target: QWidget,
        orientation: eBlindsOrientation = eBlindsOrientation.Horizontal,
        stripCount: int = C_DEFAULT_STRIPS,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(target, *args, **kwargs)
        self._orientation: eBlindsOrientation = orientation
        self._stripCount: int = max(1, int(stripCount))

    @property
    def orientation(self) -> eBlindsOrientation:
        return self._orientation

    @orientation.setter
    def orientation(self, value: eBlindsOrientation) -> None:
        self._orientation = value

    @property
    def stripCount(self) -> int:
        return self._stripCount

    @stripCount.setter
    def stripCount(self, value: int) -> None:
        self._stripCount = max(1, int(value))

    def _sizeAt(self, progress: float) -> QSize:
        """Quantize progress into strip steps along the animated axis."""
        progress = max(0.0, min(1.0, progress))
        n = self._stripCount
        # Map continuous progress to discrete strip index 0..n
        step = int(progress * n)
        if step > n:
            step = n
        stepped = step / n if n else 1.0
        if progress >= 1.0:
            stepped = 1.0

        sw, sh = self._startSize.width(), self._startSize.height()
        ew, eh = self._endSize.width(), self._endSize.height()

        if self._orientation is eBlindsOrientation.Vertical:
            w = int(round(sw + (ew - sw) * stepped))
            h = sh if eh == sh else int(round(sh + (eh - sh) * progress))
        else:
            h = int(round(sh + (eh - sh) * stepped))
            w = sw if ew == sw else int(round(sw + (ew - sw) * progress))

        return QSize(max(0, w), max(0, h))

    def _resolveEnd(
        self,
        *,
        endWidth: int | None,
        endHeight: int | None,
    ) -> None:
        self._captureStart()
        w = self._startSize.width()
        h = self._startSize.height()
        if self._orientation is eBlindsOrientation.Vertical:
            if endWidth is None:
                raise AnimationError("Vertical blinds require endWidth")
            w = max(0, int(endWidth))
            if endHeight is not None:
                h = max(0, int(endHeight))
        else:
            if endHeight is None:
                raise AnimationError("Horizontal blinds require endHeight")
            h = max(0, int(endHeight))
            if endWidth is not None:
                w = max(0, int(endWidth))
        self._endSize = QSize(w, h)
