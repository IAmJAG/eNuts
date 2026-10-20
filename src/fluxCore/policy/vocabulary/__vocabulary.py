# ==================================================================================
from __future__ import annotations

# ==================================================================================
import hashlib
from typing import Dict, List, Mapping, Union

# ==================================================================================
import torch
import torch.nn.functional as F
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel, iVocabulary
from .__label import Label

# ==================================================================================
C_DEFAULT_EMBED_DIM: int = 128


# ==================================================================================
def _idToEmbedding(labelId: str, embedDim: int) -> Tensor:
    digest = hashlib.sha256(str(labelId).encode("utf-8")).hexdigest()
    seed = int(digest[:16], 16) % (2**63 - 1)
    generator = torch.Generator()
    generator.manual_seed(seed)
    vector = torch.randn(embedDim, generator=generator, dtype=torch.float32)
    return F.normalize(vector, p=2, dim=0)


# ==================================================================================
class Vocabulary(dict, Serializable):
    """Finite discrete vocabulary: id → Label, convertible to an embedding table.

    Used for closed sets only (actions, argument kinds). Not for open argument values.
    """

    def __init__(
        self,
        vocab: Mapping[str, Union[iLabel, str]] | None = None,
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> None:
        dict.__init__(self)
        Serializable.__init__(self)

        self._embedDim: int = int(embedDim)
        if self._embedDim < 1:
            raise ValueError("embedDim must be >= 1")

        # Persisted snapshot for Serializable encode/decode
        self._entries: Dict[str, Label] = {}
        self.Properties.extend(["entries", "embedDim"])

        if vocab:
            for key, value in vocab.items():
                self._put(key, value)

    def _put(self, key: str, value: Union[iLabel, str, Label]) -> None:
        if isinstance(value, str):
            label = Label(key, value)
        elif isinstance(value, Label):
            label = value
            if not label.id:
                label.id = key
        else:
            label = Label(getattr(value, "id", key), getattr(value, "description", ""))
        dict.__setitem__(self, key, label)
        self._entries[key] = label

    def __setitem__(self, key: str, value: Union[iLabel, str, Label]) -> None:
        self._put(key, value)

    def __delitem__(self, key: str) -> None:
        dict.__delitem__(self, key)
        self._entries.pop(key, None)

    # ------------------------------------------------------------------
    @property
    def embedDim(self) -> int:
        return self._embedDim

    @embedDim.setter
    def embedDim(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("embedDim must be >= 1")
        self._embedDim = int(value)

    @property
    def entries(self) -> Dict[str, Label]:
        return self._entries

    @entries.setter
    def entries(self, value: Dict[str, Label]) -> None:
        self.clear()
        self._entries = {}
        if value:
            for key, label in value.items():
                self._put(key, label)

    @property
    def dimension(self) -> int:
        return len(self)

    @property
    def labels(self) -> List[str]:
        return list(self.keys())

    def toTensor(self) -> Tensor:
        """Embedding table [N, embedDim] in label key order."""
        if not self:
            return torch.empty(0, self._embedDim, dtype=torch.float32)
        rows = [_idToEmbedding(key, self._embedDim) for key in self.keys()]
        return torch.stack(rows, dim=0)

    def decode(self, dct) -> None:
        """Restore embedDim + entries, then rebuild the dict map."""
        Serializable.decode(self, dct)
        # Rebuild dict view from _entries after setattr in decode
        dict.clear(self)
        for key, label in list(self._entries.items()):
            if isinstance(label, dict):
                item = Label()
                item.decode(label)
                label = item
                self._entries[key] = label
            dict.__setitem__(self, key, label)
