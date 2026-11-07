# ==================================================================================
from enum import Enum

# ==================================================================================
from typing import Type, Union

# ==================================================================================
from numpy import ndarray
from PIL.Image import Image
from PySide6.QtGui import QImage
from torch import Tensor

# ==================================================================================
type DECODEFORMAT = Image | QImage | ndarray | Tensor
# ==================================================================================

# ==================================================================================
class eDecodeFormat(Enum):
    PIL = Image
    QIMAGE = QImage
    NUMPY = ndarray
    TORCH = Tensor

# ==================================================================================
__all__ = ["eDecodeFormat", "DECODEFORMAT"]