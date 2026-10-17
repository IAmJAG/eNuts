# ==================================================================================
from __future__ import annotations

# ==================================================================================
from .__blindsAnimationBase import BlindsAnimationBase
from .__eBlindsOrientation import eBlindsOrientation


# ==================================================================================
class BlindsOut(BlindsAnimationBase):
    """Collapse size in strip steps.

    ``start(endWidth=0)`` or ``start(endHeight=0)`` by orientation; defaults to 0.
    """

    def _onStart(self, *args, **kwargs) -> None:
        if self._orientation is eBlindsOrientation.Vertical:
            endWidth = kwargs.get("endWidth", 0)
            endHeight = kwargs.get("endHeight")
        else:
            endHeight = kwargs.get("endHeight", 0)
            endWidth = kwargs.get("endWidth")
        self._resolveEnd(endWidth=endWidth, endHeight=endHeight)
        self._applySize(self._startSize)
