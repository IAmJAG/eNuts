# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from ..__pixmapUtils import ImageLike, toPixmap
from .__blindsAnimationBase import BlindsAnimationBase


# ==================================================================================
class BlindsIn(BlindsAnimationBase):
    """Open blinds to reveal targetImage."""

    def _onStart(self, *args, **kwargs) -> None:
        targetImage: Optional[ImageLike] = kwargs.get("targetImage")
        if targetImage is None and args:
            targetImage = args[0]  # type: ignore[assignment]
        if targetImage is None:
            raise AnimationError("BlindsIn.start requires targetImage")

        self._content = toPixmap(targetImage)
        empty = QPixmap(max(1, self._target.width()), max(1, self._target.height()))
        empty.fill(Qt.GlobalColor.transparent)
        self._original = empty
        self._applyPixmap(self._buildFrame(0.0, self._original, self._content))

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(self._buildFrame(progress, self._original, self._content))

    def _onFinished(self) -> None:
        self._applyPixmap(self._buildFrame(1.0, self._original, self._content))
