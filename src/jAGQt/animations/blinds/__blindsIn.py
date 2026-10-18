# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from .__blindsAnimationBase import BlindsAnimationBase
from .__eBlindsOrientation import eBlindsOrientation


# ==================================================================================
class BlindsIn(BlindsAnimationBase):
    """Expand size in strip steps.

    ``start(endWidth=...)`` or ``start(endHeight=...)`` required by orientation.
    """

    def _onStart(self, *args, **kwargs) -> None:
        if self._orientation is eBlindsOrientation.Vertical:
            endWidth = kwargs.get("endWidth", args[0] if args else None)
            endHeight = kwargs.get("endHeight")
            if endWidth is None:
                raise AnimationError("BlindsIn (Vertical) requires endWidth")
        else:
            endHeight = kwargs.get("endHeight", args[0] if args else None)
            endWidth = kwargs.get("endWidth")
            if endHeight is None:
                raise AnimationError("BlindsIn (Horizontal) requires endHeight")
        self._resolveEnd(endWidth=endWidth, endHeight=endHeight)
        self._applySize(self._startSize)
