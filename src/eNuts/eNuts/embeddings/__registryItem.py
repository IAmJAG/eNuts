# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any

# ==================================================================================
from torch import Tensor


# ==================================================================================
class RegistryItem:
    def __init__(
        self, key: str, index: int,
        embedding: Tensor, metadata: dict[str, Any] | None = None,
    ):
        self._key = key
        self._index = index
        self._embedding = embedding  
        self._metadata = metadata or {}
