# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, Iterator, List, Mapping, Optional, Type, Union

# ==================================================================================
import torch
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel, iVocabulary
from ...utilities import G_DEFAULT_EMBED_DIM, deterministicEmbedding
from .labels import Label


# ==================================================================================
class Vocabulary[T: iLabel](iVocabulary, Serializable):
    """Generic discrete vocabulary. Subclasses set labelClass to the concrete Label type."""

    labelClass: Type[iLabel] = Label

    def __init__(
        self,
        vocab: Optional[Mapping[str, Union[T, str]]] = None,
        dimension: int = G_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()

        self._dimension: int = int(dimension)
        if self._dimension < 1:
            raise ValueError("dimension (embed width) must be >= 1")

        self._entries: Dict[str, T] = {}
        self.Properties.extend(["dimension", "entries"])

        if vocab:
            for key, value in vocab.items():
                self._put(key, value)

    def _put(self, key: str, value: Union[T, str, Mapping, Any]) -> None:
        LabelCls = type(self).labelClass

        if isinstance(value, str):
            label = LabelCls(key, value)

        elif isinstance(value, iLabel):
            label = value
            if not label.id or label.id != key:
                if label.id and label.id != key:
                    warning(
                        f"Vocabulary key mismatch: {key!r} != {label.id!r}; "
                        f"replacing {label.id!r} with {key!r}"
                    )
                label.id = key

        elif isinstance(value, Mapping):
            labelId = value.get("id", key)
            description = value.get("description", "")
            label = LabelCls(str(labelId or key), str(description or ""))

        else:
            label = LabelCls(
                getattr(value, "id", key), getattr(value, "description", "")
            )

        self._entries[key] = label  # type: ignore[assignment]

    # ------------------------------------------------------------------
    def __getitem__(self, key: str) -> T:
        return self._entries[key]

    def __setitem__(self, key: str, value: Union[T, str]) -> None:
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
        return self._dimension

    @dimension.setter
    def dimension(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("dimension (embed width) must be >= 1")
        self._dimension = int(value)

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> Dict[str, T]:
        return self._entries

    @property
    def labels(self) -> List[str]:
        return list(self._entries.keys())

    def labelAt(self, index: int) -> str:
        keys = self.labels
        if index < 0 or index >= len(keys):
            raise IndexError(f"label index {index} out of range (size={len(keys)})")
        return keys[index]

    def toTensor(self) -> Tensor:
        dim: int = self._dimension
        if not self._entries:
            return torch.empty(0, dim)
        rows = [
            deterministicEmbedding(label.vocabularyKey, dim)
            for label in self._entries.values()
        ]
        return torch.stack(rows, dim=0)
