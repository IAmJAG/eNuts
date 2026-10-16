# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

# ==================================================================================
from ..__pixmapUtils import ImageLike, toPixmap
from .__blindsAnimationBase import BlindsAnimationBase


# ==================================================================================
class BlindsOut(BlindsAnimationBase):
    """Close blinds over current content until cleared."""

    def _onStart(self, *args, **kwargs) -> None:
        source: Optional[ImageLike] = kwargs.get("source")
        self._original = toPixmap(source) if source is not None else self._grabTarget()
        empty = QPixmap(max(1, self._target.width()), max(1, self._target.height()))
        empty.fill(Qt.GlobalColor.transparent)
        self._content = empty
        # Progress reveals "empty" over original (blinds closing / clearing)
        self._applyPixmap(self._buildFrame(0.0, self._original, self._content))

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(self._buildFrame(progress, self._original, self._content))

    def _onFinished(self) -> None:
        self._applyPixmap(self._buildFrame(1.0, self._original, self._content))
