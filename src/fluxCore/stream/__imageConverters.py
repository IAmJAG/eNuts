# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Callable, Optional

# ==================================================================================
import numpy as np

# ==================================================================================
from av import VideoCodecContext, VideoFrame
from PySide6.QtGui import QImage
from torch import Tensor

# ==================================================================================
from fluxCore.types.interface.packets import iFrame

# ==================================================================================
from .__eDecodeFormat import eDecodeFormat


# ==================================================================================
def toPIL(frame: iFrame, codec: VideoCodecContext) -> Optional[QImage | Tensor | np.ndarray]:
    try:
        return toVideoFrame(frame, codec)

    except Exception as ex:        
        raise ex

def toQImage(frame: iFrame, codec: VideoCodecContext) -> Optional[QImage]:
    try:
        imgArray: Optional[np.ndarray] = toNumpy(frame, codec)
        if imgArray is None: return None
        height, width, channels = imgArray.shape
        bytesPerLine = channels * width
        image: QImage = QImage(imgArray.data, width, height, bytesPerLine, QImage.Format.Format_RGB888).copy()
        setattr(image, "_ownership", imgArray)
        return image

    except Exception as ex:
        raise ex

def toTensor(frame: iFrame, codec: VideoCodecContext) -> Optional[Tensor]:
    try:
        return toVideoFrame(frame, codec, True)

    except Exception as ex:
        raise ex

def toNumpy(frame: iFrame, codec: VideoCodecContext) -> Optional[np.ndarray]:
    try:
        videoFrame: Optional[VideoFrame] = toVideoFrame(frame, codec)
        if videoFrame is None: return None
        return videoFrame.to_ndarray(format="rgb24")

    except Exception as ex:
        raise ex

def toVideoFrame(frame: iFrame, codec: VideoCodecContext, gpu: bool = False) -> Optional[VideoFrame | Tensor]:
    try:
        if frame.isConfig: return None
        return frame.decode(codec, gpu)
            
    except Exception as ex:
        raise ex

# ==================================================================================
G_DECODE_FORMAT_MAP: dict[eDecodeFormat, Callable] = {
    eDecodeFormat.PIL: toPIL, eDecodeFormat.QIMAGE: toQImage,
    eDecodeFormat.NUMPY: toNumpy, eDecodeFormat.TORCH: toTensor,
}
# ==================================================================================

# ==================================================================================
__all__ = ["toPIL", "toQImage", "toTensor", "toNumpy", "G_DECODE_FORMAT_MAP"]
