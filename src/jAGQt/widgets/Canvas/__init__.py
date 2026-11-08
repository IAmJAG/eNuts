# ==================================================================================
from .__canvas import Canvas
from .__canvasBase import CanvasBase
from .__fitMode import CanvasFitMode, ImageFitMode
from .__glCanvas import GLCanvas

# ==================================================================================
# Backward-compatible aliases
Image = Canvas
GLImage = GLCanvas
ImageBase = CanvasBase

# ==================================================================================
__all__ = [
    "Canvas",
    "GLCanvas",
    "CanvasBase",
    "CanvasFitMode",
    "Image",
    "GLImage",
    "ImageBase",
    "ImageFitMode",
]
