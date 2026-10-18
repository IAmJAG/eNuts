# ==================================================================================
# src/jAGQt/animations/wipe/__wipeTransition.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from .__wipeAnimationBase import ImageLike, WipeAnimationBase, _toPixmap


# ==================================================================================
class WipeTransition(WipeAnimationBase):
    """Single continuous pass: wipe from original to target image.

    ``start(targetImage=..., originalImage=None)``
    - *targetImage* (required): ending image that remains after the wipe.
    - *originalImage* (optional): if omitted, the target widget is grabbed.
    """

    def _onStart(self, *args, **kwargs) -> None:
        targetImage: Optional[ImageLike] = kwargs.get("targetImage")
        originalImage: Optional[ImageLike] = kwargs.get("originalImage")

        if targetImage is None and len(args) >= 1:
            targetImage = args[0]  # type: ignore[assignment]
        if originalImage is None and len(args) >= 2:
            originalImage = args[1]  # type: ignore[assignment]

        if targetImage is None:
            raise AnimationError("WipeTransition.start requires targetImage")

        self._content = _toPixmap(targetImage)
        if originalImage is None:
            self._original = self._grabTarget()
        else:
            self._original = _toPixmap(originalImage)

        self._applyPixmap(self._buildFrame(0.0, self._original, self._content))

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(self._buildFrame(progress, self._original, self._content))

    def _onFinished(self) -> None:
        self._applyPixmap(self._buildFrame(1.0, self._original, self._content))
