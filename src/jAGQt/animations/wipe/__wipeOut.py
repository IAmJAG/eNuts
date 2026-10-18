# ==================================================================================
# src/jAGQt/animations/wipe/__wipeOut.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtGui import QPixmap

# ==================================================================================
from .__wipeAnimationBase import ImageLike, WipeAnimationBase, _toPixmap


# ==================================================================================
class WipeOut(WipeAnimationBase):
    """Wipe away the target's current (or provided) content under a visible blade."""

    def _onStart(self, *args, **kwargs) -> None:
        source: Optional[ImageLike] = kwargs.get("source")
        if source is not None:
            self._original = _toPixmap(source)
        else:
            self._original = self._grabTarget()
        self._content = QPixmap()  # revealed region becomes empty
        self._applyPixmap(self._buildFrame(0.0, self._original, self._content))

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(self._buildFrame(progress, self._original, self._content))

    def _onFinished(self) -> None:
        self._applyPixmap(self._buildFrame(1.0, self._original, self._content))
