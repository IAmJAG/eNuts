# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
from typing import Any, Optional, Protocol, Union, runtime_checkable

# ==================================================================================
from torch import Tensor
from torch import device as TorchDevice


# ==================================================================================
@runtime_checkable
class iPolicy(Protocol):
    def forward(self, *args, **kwargs) -> dict[str, Tensor]: ...
    def predict(self, *args, **kwargs) -> tuple[str, dict[str, Any]]: ...
    def save(self, path: str | Path) -> None: ...    
    @classmethod
    def load(self, path: str | Path, device: Optional[Union[str, TorchDevice]] = "cuda",) -> iPolicy: ...
