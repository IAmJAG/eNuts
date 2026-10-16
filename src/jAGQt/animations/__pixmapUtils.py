# ==================================================================================
# src/jAGQt/animations/__pixmapUtils.py
# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Optional, Union

# ==================================================================================
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget

# ==================================================================================
from jAGQt.utilities import AnimationError

# ==================================================================================
ImageLike = Union[QPixmap, QImage, str]
# ==================================================================================


# ==================================================================================
def assertSetPixmap(target: QWidget) -> None:
    if target is None:
        raise AnimationError("Animation target must not be None")
    if not callable(getattr(target, "setPixmap", None)):
        raise AnimationError(
            f"Target {type(target).__name__} does not support setPixmap; "
            f"use QLabel-based widgets (e.g. Icon)"
        )


def toPixmap(source: Optional[ImageLike]) -> QPixmap:
    if source is None:
        return QPixmap()
    if isinstance(source, QPixmap):
        return source
    if isinstance(source, QImage):
        return QPixmap.fromImage(source)
    if isinstance(source, str):
        px = QPixmap(source)
        if px.isNull():
            raise AnimationError(f"Failed to load image from path: {source!r}")
        return px
    raise AnimationError(f"Unsupported image type: {type(source).__name__}")


def grabWidget(target: QWidget) -> QPixmap:
    grab = target.grab()
    if grab.isNull():
        w = max(1, target.width())
        h = max(1, target.height())
        grab = QPixmap(w, h)
        grab.fill(Qt.GlobalColor.transparent)
    return grab


def scaleToTarget(pixmap: QPixmap, target: QWidget) -> QPixmap:
    if pixmap.isNull():
        return pixmap
    size = target.size()
    if size.width() <= 0 or size.height() <= 0:
        return pixmap
    return pixmap.scaled(
        size,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def applyPixmap(target: QWidget, pixmap: QPixmap) -> None:
    assertSetPixmap(target)
    target.setPixmap(pixmap)  # type: ignore[attr-defined]
