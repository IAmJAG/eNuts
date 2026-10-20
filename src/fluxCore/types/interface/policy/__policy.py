# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iPolicy(Protocol):
    def forward(self, imageArray: Tensor) -> dict[str, Tensor]: ...
    def predict(self, imageArray: Tensor) -> tuple[str, dict[str, Any]]: ...
