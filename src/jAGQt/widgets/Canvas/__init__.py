# ==================================================================================
from ...types.__eFitMode import CanvasFitMode, ImageFitMode
from .__canvas import Canvas
from .__canvasBase import CanvasBase
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
