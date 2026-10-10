# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, List

# ==================================================================================
from torch import Tensor, cuda, stack
from torch import device as tDevice
from torch import empty as tEmpty

# ==================================================================================
from ....types.interface.embeddings.registry import iRegistry, iRegistryItem
from .__registryItem import RegistryItem


# ==================================================================================
class Registry(iRegistry):
    def __init__(self, dimension: int, device: tDevice | str = "cuda") -> None: 
        self._embeddingDim = dimension
        self._itemsByKey: Dict[str, iRegistryItem] = dict[str, iRegistryItem]()
        self._itemsByIndex: List[iRegistryItem] = list[iRegistryItem]()

        self._device: tDevice
        if isinstance(device, str):
            if device.startswith("cuda") and not cuda.is_available(): device = "cpu"
            self._device = tDevice(device)

        else:
            self._device = device
    
    def register(self, key: str, embedding: Tensor, metadata: Dict[str, Any] = {}) -> int:
        if embedding.shape[-1] != self._embeddingDim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self._embeddingDim}, got {embedding.shape[-1]}"
            )

        item: iRegistryItem = self._itemsByKey.get(key, None)
        if item is not None:            
            item.embedding = embedding.detach().to(self._device)
            if metadata: item.metadata.update(metadata)
            return item.index
        
        index = len(self._itemsByIndex)
        item = RegistryItem(
            key=key, index=index, embedding=embedding.detach().to(self._device), metadata=metadata
        )
        self._itemsByKey[key] = item
        self._itemsByIndex.append(item)
        return index

    def get(self, key: str) -> RegistryItem:
        if key not in self._itemsByKey:
            raise KeyError(f"Registry key not found: {key}")

        return self._itemsByKey[key]

    def getByIndex(self, index: int) -> RegistryItem:
        if index < 0 or index >= len(self._itemsByIndex):
            raise IndexError(f"Registry index out of range: {index}")
        return self._itemsByIndex[index]

    def getIndex(self, key: str) -> int:
        return self.get(key).index

    def getEmbeddings(self) -> Tensor:
        if not self._itemsByIndex: return tEmpty((0, self._embeddingDim))
        return stack([item.embedding for item in self._itemsByIndex], dim=0)

    def __len__(self) -> int:
        return len(self._itemsByIndex)