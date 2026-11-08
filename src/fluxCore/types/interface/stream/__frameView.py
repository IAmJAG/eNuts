# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iFrameView(Protocol):
    def present(self, frame: Tensor | object) -> bool:...
    def clear(self) -> None: ...