# ==================================================================================
from __future__ import annotations

# ==================================================================================
from PySide6.QtCore import QSize

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from .__blindsAnimationBase import BlindsAnimationBase
from .__eBlindsOrientation import eBlindsOrientation


# ==================================================================================
class BlindsTransition(BlindsAnimationBase):
    """Stepped size transition from current (or start*) to end*.

    ``start(endWidth=..., endHeight=..., startWidth=optional, startHeight=optional)``
    """

    def _onStart(self, *args, **kwargs) -> None:
        if self._orientation is eBlindsOrientation.Vertical:
            endWidth = kwargs.get("endWidth", args[0] if args else None)
            endHeight = kwargs.get("endHeight")
            if endWidth is None:
                raise AnimationError("BlindsTransition (Vertical) requires endWidth")
        else:
            endHeight = kwargs.get("endHeight", args[0] if args else None)
            endWidth = kwargs.get("endWidth")
            if endHeight is None:
                raise AnimationError("BlindsTransition (Horizontal) requires endHeight")

        self._resolveEnd(endWidth=endWidth, endHeight=endHeight)

        startWidth = kwargs.get("startWidth")
        startHeight = kwargs.get("startHeight")
        if startWidth is not None or startHeight is not None:
            w = int(startWidth) if startWidth is not None else self._startSize.width()
            h = int(startHeight) if startHeight is not None else self._startSize.height()
            self._startSize = QSize(max(0, w), max(0, h))

        self._applySize(self._startSize)
