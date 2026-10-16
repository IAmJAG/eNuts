# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

# ==================================================================================
from ..__pixmapUtils import ImageLike, toPixmap
from .__drawerAnimationBase import DrawerAnimationBase


# ==================================================================================
class DrawerOut(DrawerAnimationBase):
    """Slide current content off-screen like a closing drawer."""

    def _onStart(self, *args, **kwargs) -> None:
        source: Optional[ImageLike] = kwargs.get("source")
        if source is not None:
            self._original = toPixmap(source)
        else:
            self._original = self._grabTarget()
        empty = QPixmap(max(1, self._target.width()), max(1, self._target.height()))
        empty.fill(Qt.GlobalColor.transparent)
        self._content = empty
        self._applyPixmap(
            self._buildFrame(0.0, self._content, self._original, slideIn=False)
        )

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(
            self._buildFrame(progress, self._content, self._original, slideIn=False)
        )

    def _onFinished(self) -> None:
        self._applyPixmap(
            self._buildFrame(1.0, self._content, self._original, slideIn=False)
        )
