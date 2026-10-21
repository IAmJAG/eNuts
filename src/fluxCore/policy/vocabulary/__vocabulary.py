# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List, Mapping, Optional, Union

# ==================================================================================
import torch
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel, iVocabulary
from ...utilities import G_DEFAULT_EMBED_DIM, deterministicEmbedding
from .__label import Label


# ==================================================================================
class Vocabulary(iVocabulary, Serializable):
    def __init__(
        self,
        vocab: Optional[Mapping[str, Union[iLabel, str]]],
        dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()

        self._dimension: int = int(dimension)
        if self._dimension < 1:
            raise ValueError("embedDim must be >= 1")

        self._entries: Dict[str, Label] = {}        
        self.Properties.extend(["entries", "dimension"])

        if vocab:
            for key, value in vocab.items():
                self._put(key, value)

    def _put(self, key: str, value: Union[iLabel, str]) -> None:
        if isinstance(value, str): label = Label(key, value)

        elif isinstance(value, Label):            
            label: iLabel = value
            if not label.id or label.id != key:
                if label.id != key:
                    warning(f"Vocabulary key mismatch: {key!r} != {label.id!r}; replacing {label.id!r} with {key!r}")
                label.id = key

        else:
            label = Label(getattr(value, "id", key), getattr(value, "description", ""))

        self._entries[key] = label

    def __setitem__(self, key: str, value: Union[iLabel, str, Label]) -> None:
        self._put(key, value)

    def __delitem__(self, key: str) -> None:        
        self._entries.pop(key, None)

    # ------------------------------------------------------------------
    @property
    def dimension(self) -> int:
        return self._dimension

    @dimension.setter
    def dimension(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("dimension must be >= 1")
        
        self._dimension = int(value)

    @property
    def entries(self) -> Dict[str, Label]:
        return self._entries

    @entries.setter
    def entries(self) -> int:
        return self._entries

    @property
    def labels(self) -> List[str]:
        return list(self._entries.keys())

    def toTensor(self) -> Tensor:
        dim: int = self._dimension
        if self._entries is None or len(self._entries) < 1:
            return torch.empty(0, dim)
        rows = [deterministicEmbedding(label.vocabularyKey, dim) for _, label in self._entries.items()]
        return torch.stack(rows, dim=0)
