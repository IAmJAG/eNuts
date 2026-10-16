# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from ..__pixmapUtils import ImageLike, toPixmap
from .__blindsAnimationBase import BlindsAnimationBase


# ==================================================================================
class BlindsTransition(BlindsAnimationBase):
    """Single pass: blinds open from original to targetImage.

    ``start(targetImage=..., originalImage=None)``
    """

    def _onStart(self, *args, **kwargs) -> None:
        targetImage: Optional[ImageLike] = kwargs.get("targetImage")
        originalImage: Optional[ImageLike] = kwargs.get("originalImage")
        if targetImage is None and len(args) >= 1:
            targetImage = args[0]  # type: ignore[assignment]
        if originalImage is None and len(args) >= 2:
            originalImage = args[1]  # type: ignore[assignment]
        if targetImage is None:
            raise AnimationError("BlindsTransition.start requires targetImage")

        self._content = toPixmap(targetImage)
        self._original = (
            self._grabTarget() if originalImage is None else toPixmap(originalImage)
        )
        self._applyPixmap(self._buildFrame(0.0, self._original, self._content))

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(self._buildFrame(progress, self._original, self._content))

    def _onFinished(self) -> None:
        self._applyPixmap(self._buildFrame(1.0, self._original, self._content))
