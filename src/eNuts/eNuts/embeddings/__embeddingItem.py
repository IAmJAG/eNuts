# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.embeddings import iEmbeddingItem


# ==================================================================================
class iEmbeddingItem(Serializable, iEmbeddingItem):
    def __init__(self, key: str, description: str): 
        super().__init__()
        self._key = key
        self._description = description
        self.Properties.extend(["key", "description"])

    @property
    def key(self) -> str: 
        return self._key
    
    @property
    def description(self) -> str: 
        return self._description
