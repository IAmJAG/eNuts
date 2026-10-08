# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iPolicyNet(Protocol):
    def __init__(self, options: dict[str, Any] | None = None): ...
    def forward(self) -> Tensor: ...
    def extractFrameFeatures(self, frameTensor): ...