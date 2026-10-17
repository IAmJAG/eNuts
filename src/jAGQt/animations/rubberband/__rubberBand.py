# ==================================================================================
# src/jAGQt/animations/rubberband/__rubberBand.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QEasingCurve, QSize
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from ..__sizeAnimationBase import SizeAnimationBase


# ==================================================================================
def _elastic01(t: float, amplitude: float = 1.0, period: float = 0.3) -> float:
    """Out-elastic mapping of t in [0,1] → slightly overshoots 1.0 then settles."""
    if t <= 0.0:
        return 0.0
    if t >= 1.0:
        return 1.0
    import math

    p = period if period > 0 else 0.3
    a = amplitude if amplitude >= 1.0 else 1.0
    s = p / 4.0 if a < 1.0 else p / (2.0 * math.pi) * math.asin(1.0 / a)
    return a * math.pow(2.0, -10.0 * t) * math.sin((t - s) * (2.0 * math.pi) / p) + 1.0


# ==================================================================================
class RubberBand(SizeAnimationBase):
    """Resize a widget with rubber-band (elastic overshoot) motion.

    ``start(endWidth=..., endHeight=..., startWidth=optional, startHeight=optional,
            overshoot=1.0)``

    At least one of endWidth / endHeight must differ from the start size.
    Default easing on the driver is still used for time; the size curve applies
    an additional elastic map so the widget overshoots then settles on the end size.
    """

    def __init__(
        self,
        target: QWidget,
        *args,
        **kwargs,
    ) -> None:
        # Prefer OutCubic on the driver; elastic is applied in _sizeAt
        kwargs.setdefault("easing", QEasingCurve.Type.Linear)
        super().__init__(target, *args, **kwargs)
        self._overshoot: float = 1.0

    def _onStart(self, *args, **kwargs) -> None:
        self._captureStart()
        endWidth = kwargs.get("endWidth")
        endHeight = kwargs.get("endHeight")
        if endWidth is None and endHeight is None and args:
            # allow start(endWidth) or start(endWidth, endHeight)
            endWidth = args[0]
            if len(args) >= 2:
                endHeight = args[1]

        startWidth = kwargs.get("startWidth")
        startHeight = kwargs.get("startHeight")
        if startWidth is not None or startHeight is not None:
            w = int(startWidth) if startWidth is not None else self._startSize.width()
            h = int(startHeight) if startHeight is not None else self._startSize.height()
            self._startSize = QSize(max(0, w), max(0, h))

        w = int(endWidth) if endWidth is not None else self._startSize.width()
        h = int(endHeight) if endHeight is not None else self._startSize.height()
        self._endSize = QSize(max(0, w), max(0, h))

        if self._startSize == self._endSize:
            raise AnimationError("RubberBand start and end sizes must differ")

        self._overshoot = float(kwargs.get("overshoot", 1.0))
        self._applySize(self._startSize)

    def _sizeAt(self, progress: float) -> QSize:
        progress = max(0.0, min(1.0, progress))
        t = _elastic01(progress, amplitude=max(1.0, self._overshoot))
        # Clamp visual size to non-negative; slight overshoot past end is intentional
        sw, sh = self._startSize.width(), self._startSize.height()
        ew, eh = self._endSize.width(), self._endSize.height()
        w = int(round(sw + (ew - sw) * t))
        h = int(round(sh + (eh - sh) * t))
        return QSize(max(0, w), max(0, h))
