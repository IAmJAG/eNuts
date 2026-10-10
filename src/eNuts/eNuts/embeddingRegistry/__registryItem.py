# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict

# ==================================================================================
from torch import Tensor
from torch import device as tDevice


# ==================================================================================
class RegistryItem:
    def __init__(
        self, key: str, index: int,
        embedding: Tensor, metadata: Dict[str, Any] = dict[str, Any]()
    ):
        self._key: str = key
        self._index: int = index
        self._embedding: Tensor = embedding  
        self._metadata: Dict[str, Any] = metadata or dict[str, Any]()

    @property
    def key(self) -> str:
        return self._key

    @property
    def index(self) -> int:
        return self._index

    @property
    def embedding(self) -> Tensor:
        return self._embedding

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata
