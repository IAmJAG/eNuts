# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, Iterator, List, Mapping, Optional, Union

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

    Entries are persisted as plain {id, description} maps so decode does not
    depend on nested Label __type__ resolution through the serializer.
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
        # dimension only via base Properties; entries handled in encode/decode
        self.Properties.extend(["dimension"])

        if vocab:
            for key, value in vocab.items():
                self._put(key, value)

    def _put(self, key: str, value: Union[iLabel, str, Mapping, Any]) -> None:
        if isinstance(value, str):
            label = Label(key, value)

        elif isinstance(value, Label):
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
            label = Label(str(labelId or key), str(description or ""))

        else:
            label = Label(getattr(value, "id", key), getattr(value, "description", ""))

        self._entries[key] = label

    # ------------------------------------------------------------------
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
    def entries(self) -> Dict[str, Label]:
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

    # ------------------------------------------------------------------
    def encode(self) -> Dict[str, object]:
        """Persist dimension + plain entry maps (no nested Label __type__)."""
        moduleParts = self.__module__.split(".")
        if moduleParts and moduleParts[-1].startswith("__"):
            moduleParts = moduleParts[:-1]
        modulePath = ".".join(moduleParts)

        return {
            "dimension": self._dimension,
            "entries": {
                key: {"id": label.id, "description": label.description}
                for key, label in self._entries.items()
            },
            "__type__": f"{modulePath}.{type(self).__name__}",
        }

    def decode(self, dct: Any) -> None:
        """Restore dimension and rebuild Labels from plain entry maps."""
        if not isinstance(dct, dict):
            raise TypeError(f"Vocabulary.decode expects dict, got {type(dct)!r}")

        dimension = dct.get("dimension", G_DEFAULT_EMBED_DIM)
        self._dimension = int(dimension)
        if self._dimension < 1:
            raise ValueError("dimension (embed width) must be >= 1")

        self._entries = {}
        rawEntries = dct.get("entries") or {}
        if not isinstance(rawEntries, dict):
            raise TypeError(
                f"Vocabulary.entries must be a dict, got {type(rawEntries)!r}"
            )

        for key, value in rawEntries.items():
            self._put(str(key), value)
