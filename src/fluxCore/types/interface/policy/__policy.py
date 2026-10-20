# ==================================================================================
from typing import Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iPolicy(Protocol):
    def forward(self, imageArray: Tensor) -> Tensor: ...
    def predict(self, imageArray: Tensor) -> str: ...
