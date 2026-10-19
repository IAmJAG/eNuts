# ==================================================================================
# src/fluxCore/types/interface/policy/__policy.py
# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iPolicy(Protocol):
    def forward(self, image: Tensor) -> Tensor: ...
    def predict(self, image: Tensor) -> str: ...
    def reset(self) -> None: ...
