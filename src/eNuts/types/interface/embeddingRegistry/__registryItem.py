# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor


# ==================================================================================
@runtime_checkable
class iRegistryItem(Protocol):
    def __init__(
        self, key: str, index: int,
        embedding: Tensor, metadata: Dict[str, Any] = {},
    ): ...
    @property
    def key(self) -> str: ...
    @property
    def index(self) -> int: ...
    @property
    def embedding(self) -> Tensor: ...
    @property
    def metadata(self) -> dict[str, Any]: ...
