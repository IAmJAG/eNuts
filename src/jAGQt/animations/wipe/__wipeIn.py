# ==================================================================================
# src/jAGQt/animations/wipe/__wipeIn.py
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
from .__wipeAnimationBase import ImageLike, WipeAnimationBase, _toPixmap


# ==================================================================================
class WipeIn(WipeAnimationBase):
    """Reveal content onto the target under a visible blade."""

    def _onStart(self, *args, **kwargs) -> None:
        targetImage: Optional[ImageLike] = kwargs.get("targetImage")
        if targetImage is None and args:
            targetImage = args[0]  # type: ignore[assignment]
        if targetImage is None:
            raise AnimationError("WipeIn.start requires targetImage")

        self._content = _toPixmap(targetImage)
        # Underneath starts empty (transparent)
        w = max(1, self._target.width())
        h = max(1, self._target.height())
        empty = QPixmap(w, h)
        empty.fill(Qt.GlobalColor.transparent)
        self._original = empty
        self._applyPixmap(self._buildFrame(0.0, self._original, self._content))

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(self._buildFrame(progress, self._original, self._content))

    def _onFinished(self) -> None:
        self._applyPixmap(self._buildFrame(1.0, self._original, self._content))
