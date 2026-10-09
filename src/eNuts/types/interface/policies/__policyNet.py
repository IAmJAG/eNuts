# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iPolicyNet(Protocol):
    def __init__(self, options: dict[str, Any] | None = None) -> None: ...
    def forward(self, intentEmbedding: Tensor, previousActionEmbedding: Tensor) -> Tensor: ...
    def extractFrameFeatures(self, frameTensor: Tensor) -> Tensor: ...
    def save(self, path, optimizer=None) -> None: ...
    @classmethod
    def load(cls, path, device="CUDA", optimizer=None) -> tuple[iPolicyNet, dict[str, object]]: ...
