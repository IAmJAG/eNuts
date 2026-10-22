# ==================================================================================
from __future__ import annotations

# ==================================================================================
from collections import deque
from typing import Any, Deque, Optional, Union

# ==================================================================================
import numpy as np
import torch
import torch.nn.functional as F
from torch import Tensor
from torch import device as TorchDevice

# ==================================================================================
from .__policy import Policy
from .__policyOptions import PolicyOptions

# ==================================================================================
C_FRAME_SIZE: int = 224


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

        self._carousel: Deque[Tensor] = deque(maxlen=self._stackSize)
        self._lastAcceptTime: Optional[float] = None
        self._blank: Tensor = torch.zeros(
            3, C_FRAME_SIZE, C_FRAME_SIZE,
            dtype=torch.float32, device=self._device,
        )

    # ------------------------------------------------------------------
    def reset(self) -> None:
        self._carousel.clear()
        self._lastAcceptTime = None

    def step(
        self, frame: Union[Tensor, np.ndarray], timestamp: float,
    ) -> Optional[tuple[str, dict[str, Any]]]:
        if not self._shouldAccept(float(timestamp)):
            return None

        processed = self._preprocess(frame)
        self._carousel.append(processed)
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

    def _preprocess(self, frame: Union[Tensor, np.ndarray]) -> Tensor:
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

        if float(tensor.max()) > 1.5:
            tensor = tensor / 255.0

        tensor = tensor.to(device=self._device, dtype=torch.float32).unsqueeze(0)
        tensor = F.interpolate(
            tensor,
            size=(C_FRAME_SIZE, C_FRAME_SIZE),
            mode="bilinear",
            align_corners=False,
        )
        return tensor.squeeze(0).contiguous()
