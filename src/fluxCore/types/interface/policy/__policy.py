# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iPolicy(Protocol):
    def forward(self, imageArray: Tensor) -> tuple[Tensor, Tensor]: ...
    def predict(self, imageArray: Tensor) -> tuple[str, Tensor]: ...
