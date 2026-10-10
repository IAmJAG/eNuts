# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.embeddings import iEmbeddingItem


# ==================================================================================
class Embedding(Serializable, List[iEmbeddingItem]):
    def __init__(self, name: str, dimension: int, *args, **kwargs): 
        super().__init__(*args, **kwargs)
        self._dimension: int = dimension
        self._name: str = name
        self.Properties.extend(["dimension", "name"])

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def name(self) -> str:
        return self._name