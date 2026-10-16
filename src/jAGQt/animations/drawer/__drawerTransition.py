# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
from ..__pixmapUtils import ImageLike, toPixmap
from .__drawerAnimationBase import DrawerAnimationBase


# ==================================================================================
class DrawerTransition(DrawerAnimationBase):
    """Single pass: original slides out while target slides in from the same direction.

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
            raise AnimationError("DrawerTransition.start requires targetImage")

        self._content = toPixmap(targetImage)
        self._original = (
            self._grabTarget() if originalImage is None else toPixmap(originalImage)
        )
        self._applyPixmap(self._compose(0.0))

    def _compose(self, progress: float):
        # Original exits (slideIn=False); new enters (slideIn=True) in one frame.
        progress = max(0.0, min(1.0, progress))
        w = max(1, self._target.width())
        h = max(1, self._target.height())
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPainter, QPixmap

        from ..__pixmapUtils import scaleToTarget

        frame = QPixmap(w, h)
        frame.fill(Qt.GlobalColor.transparent)
        under = scaleToTarget(self._original, self._target)
        over = scaleToTarget(self._content, self._target)
        painter = QPainter(frame)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        if not under.isNull():
            ox, oy = self._offset(w, h, progress, slideIn=False)
            painter.drawPixmap(int(ox), int(oy), under)
        if not over.isNull():
            ox, oy = self._offset(w, h, progress, slideIn=True)
            painter.drawPixmap(int(ox), int(oy), over)
        painter.end()
        return frame

    def _onProgress(self, progress: float) -> None:
        self._applyPixmap(self._compose(progress))

    def _onFinished(self) -> None:
        self._applyPixmap(self._compose(1.0))
