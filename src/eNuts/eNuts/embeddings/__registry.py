# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any

import torch
from torch import Tensor


class Registry:
    """
    Manages intents or actions, mapping string identifiers to stable integer indices
    and dense embedding vectors.
    """

    def __init__(self, embeddingDim: int) -> None:
        self._embeddingDim = embeddingDim
        self._itemsByKey: dict[str, RegistryItem] = {}
        self._itemsByIndex: list[RegistryItem] = []

    def register(
        self, key: str, embedding: Tensor, metadata: dict[str, Any] | None = None
    ) -> int:
        """Registers a new item or updates its embedding, returning its stable index."""
        if embedding.shape[-1] != self._embeddingDim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self._embeddingDim}, got {embedding.shape[-1]}"
            )

        if key in self._itemsByKey:
            # Update existing item embedding/metadata
            item = self._itemsByKey[key]
            item.embedding = embedding.detach().cpu()
            if metadata:
                item.metadata.update(metadata)
            return item.index

        # Create new item with a stable index based on insertion order
        index = len(self._itemsByIndex)
        item = RegistryItem(
            key=key, index=index, embedding=embedding.detach().cpu(), metadata=metadata
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
        """Returns all registry embeddings stacked as [N, D] for policy action scoring."""
        if not self._itemsByIndex:
            return torch.empty((0, self._embeddingDim))
        return torch.stack([item.embedding for item in self._itemsByIndex], dim=0)

    def __len__(self) -> int:
        return len(self._itemsByIndex)