# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections import deque
from typing import Any, Deque, Optional, Union

# ==================================================================================
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torch import device as TorchDevice

# ==================================================================================
from .__policy import Policy
from .__policyOptions import PolicyOptions

# ==================================================================================
C_FRAME_SIZE: int = 224
# ImageNet stats — matches MobileNet_V3_Small_Weights.DEFAULT training
C_IMAGENET_MEAN: tuple[float, float, float] = (0.485, 0.456, 0.406)
C_IMAGENET_STD: tuple[float, float, float] = (0.229, 0.224, 0.225)


# ==================================================================================
class FrameTransformHead(nn.Module):
    """Classifier-style frame prep: layout → [0,1] → resize → ImageNet normalize.

    Input:  CHW or NCHW float/uint-scale tensor on any device
    Output: same batch rank, size (…, 3, frameSize, frameSize), normalized
    """

    def __init__(self, frameSize: int = C_FRAME_SIZE) -> None:
        super().__init__()
        self._frameSize = int(frameSize)
        self.register_buffer(
            "_mean",
            torch.tensor(C_IMAGENET_MEAN, dtype=torch.float32).view(1, 3, 1, 1),
        )
        self.register_buffer(
            "_std",
            torch.tensor(C_IMAGENET_STD, dtype=torch.float32).view(1, 3, 1, 1),
        )

    def forward(self, images: Tensor) -> Tensor:
        if images.ndim == 3:
            images = images.unsqueeze(0)
            squeeze = True
        elif images.ndim == 4:
            squeeze = False
        else:
            raise ValueError(
                f"FrameTransformHead expects CHW or NCHW, got shape {tuple(images.shape)}"
            )

        images = images.float()
        if float(images.max()) > 1.5:
            images = images / 255.0

        images = F.interpolate(
            images,
            size=(self._frameSize, self._frameSize),
            mode="bilinear",
            align_corners=False,
        )
        images = (images - self._mean) / self._std
        if squeeze:
            return images.squeeze(0)
        return images


# ==================================================================================
class StreamingPolicy(Policy):
    def __init__(
        self, options: PolicyOptions,
        device: Optional[Union[str, TorchDevice]] = "cuda",
    ) -> None:
        super().__init__(options, device=device)

        self._stackSize: int = int(options.stackSize)
        self._durationSec: float = float(options.durationSec)
        self._minAcceptInterval: float = self._durationSec / float(self._stackSize)

        self._transformHead = FrameTransformHead(C_FRAME_SIZE)
        self._transformHead.to(self._device)

        self._carousel: Deque[Tensor] = deque(maxlen=self._stackSize)
        self._lastAcceptTime: Optional[float] = None

        # Blank = transformed black frame (same space as real frames)
        black = torch.zeros(
            3, C_FRAME_SIZE, C_FRAME_SIZE, dtype=torch.float32, device=self._device
        )
        with torch.no_grad():
            self._blank = self._transformHead(black).detach()

    # ------------------------------------------------------------------
    def reset(self) -> None:
        self._carousel.clear()
        self._lastAcceptTime = None

    def step(
        self, frame: Union[Tensor, np.ndarray], timestamp: float,
    ) -> Optional[tuple[str, dict[str, Any]]]:
        if not self._shouldAccept(float(timestamp)):
            return None

        processed = self._transformHead(self._toCHW(frame))
        self._carousel.append(processed.detach())
        self._lastAcceptTime = float(timestamp)

        stack = self._buildStack()
        return self.predict(stack)

    # ------------------------------------------------------------------
    def _shouldAccept(self, timestamp: float) -> bool:
        if self._lastAcceptTime is None: return True
        return (timestamp - self._lastAcceptTime) >= self._minAcceptInterval

    def _buildStack(self) -> Tensor:
        frames: list[Tensor] = []
        missing = self._stackSize - len(self._carousel)
        if missing > 0: frames.extend([self._blank for _ in range(missing)])
        frames.extend(list(self._carousel))
        return torch.stack(frames, dim=0)

    def _toCHW(self, frame: Union[Tensor, np.ndarray]) -> Tensor:
        """ndarray | Tensor → float CHW on self._device (no normalize/resize)."""
        if isinstance(frame, np.ndarray):
            tensor = torch.from_numpy(np.ascontiguousarray(frame))

        elif isinstance(frame, Tensor):
            tensor = frame.detach()

        else:
            raise TypeError(
                f"frame must be numpy.ndarray or torch.Tensor, got {type(frame)!r}"
            )

        tensor = tensor.float()
        if tensor.ndim == 2:
            tensor = tensor.unsqueeze(0).expand(3, -1, -1).clone()

        elif tensor.ndim == 3:
            if tensor.shape[0] in (1, 3):
                pass

            elif tensor.shape[-1] in (1, 3):
                tensor = tensor.permute(2, 0, 1)

            else:
                raise ValueError(f"Cannot interpret frame shape {tuple(tensor.shape)}")

            if tensor.shape[0] == 1:
                tensor = tensor.expand(3, -1, -1).clone()

        else:
            raise ValueError(f"Expected 2D or 3D frame, got shape {tuple(tensor.shape)}")

        if tensor.shape[0] != 3:
            raise ValueError(
                f"Expected 3 channels after layout fix, got {tensor.shape[0]}"
            )

        return tensor.to(device=self._device, dtype=torch.float32)
