# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, Iterator, List, Mapping, Optional, Union

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
    """Finite discrete vocabulary.

    - dimension: embedding width (embedDim)
    - size / len: number of labels (N)
    - toTensor(): [N, dimension]
    """

    def __init__(
        self,
        vocab: Optional[Mapping[str, Union[iLabel, str]]] = None,
        dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()

        self._dimension: int = int(dimension)
        if self._dimension < 1:
            raise ValueError("dimension (embed width) must be >= 1")

        self._entries: Dict[str, Label] = {}
        self.Properties.extend(["entries", "dimension"])

        if vocab:
            for key, value in vocab.items():
                self._put(key, value)

    def _put(self, key: str, value: Union[iLabel, str]) -> None:
        if isinstance(value, str):
            label = Label(key, value)

        elif isinstance(value, Label):
            label: iLabel = value
            if not label.id or label.id != key:
                if label.id != key:
                    warning(
                        f"Vocabulary key mismatch: {key!r} != {label.id!r}; "
                        f"replacing {label.id!r} with {key!r}"
                    )
                label.id = key

        else:
            label = Label(getattr(value, "id", key), getattr(value, "description", ""))

        self._entries[key] = label

    # ------------------------------------------------------------------
    # Mapping surface (str keys only — use labels[i] / labelAt(i) for index)
    def __getitem__(self, key: str) -> Label:
        return self._entries[key]

    def __setitem__(self, key: str, value: Union[iLabel, str, Label]) -> None:
        self._put(key, value)

    def __delitem__(self, key: str) -> None:
        self._entries.pop(key, None)

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[str]:
        return iter(self._entries)

    def __contains__(self, key: object) -> bool:
        return key in self._entries

    # ------------------------------------------------------------------
    @property
    def dimension(self) -> int:
        """Embedding width (embedDim), not the label count."""
        return self._dimension

    @dimension.setter
    def dimension(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("dimension (embed width) must be >= 1")
        self._dimension = int(value)

    @property
    def size(self) -> int:
        """Number of labels (N)."""
        return len(self._entries)

    @property
    def entries(self) -> Dict[str, Label]:
        return self._entries

    @entries.setter
    def entries(self, value: Dict[str, Label] | None) -> None:
        self._entries = {}
        if not value:
            return
        for key, item in value.items():
            self._put(key, item)

    @property
    def labels(self) -> List[str]:
        return list(self._entries.keys())

    def labelAt(self, index: int) -> str:
        keys = self.labels
        if index < 0 or index >= len(keys):
            raise IndexError(f"label index {index} out of range (size={len(keys)})")
        return keys[index]

    def toTensor(self) -> Tensor:
        """Embedding table shaped [N, dimension]."""
        dim: int = self._dimension
        if not self._entries:
            return torch.empty(0, dim)
        rows = [
            deterministicEmbedding(label.vocabularyKey, dim)
            for label in self._entries.values()
        ]
        return torch.stack(rows, dim=0)
