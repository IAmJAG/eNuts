# ==================================================================================
from __future__ import annotations

# ==================================================================================
from pathlib import Path
from typing import Any, Optional, Protocol, Union, runtime_checkable

# ==================================================================================
from torch import Tensor, nn
from torch import device as torchDevice


# ==================================================================================
@runtime_checkable
class iPolicy(Protocol):
    def forward(self, *args, **kwargs) -> dict[str, Tensor]: ...    
    def save(self, path: str | Path) -> None: ...    
    @classmethod
    def load(cls, path: str | Path, module: nn.Module = None, device: Optional[Union[str, torchDevice]] = "cuda",) -> iPolicy: ...
