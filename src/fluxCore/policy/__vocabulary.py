# ==================================================================================
from __future__ import annotations

# ==================================================================================
import hashlib
from typing import Sequence

# ==================================================================================
import torch
import torch.nn.functional as F
from torch import Tensor

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
C_DEFAULT_EMBED_DIM: int = 128


# ==================================================================================
def labelToEmbedding(label: str, embedDim: int) -> Tensor:
    """Deterministic unit vector from a single label string."""
    if embedDim < 1:
        raise ValueError("embedDim must be >= 1")
    digest = hashlib.sha256(str(label).encode("utf-8")).hexdigest()
    seed = int(digest[:16], 16) % (2**63 - 1)
    generator = torch.Generator()
    generator.manual_seed(seed)
    vector = torch.randn(embedDim, generator=generator, dtype=torch.float32)
    return F.normalize(vector, p=2, dim=0)


def labelsToEmbeddings(labels: Sequence[str], embedDim: int) -> Tensor:
    """Stack deterministic unit embeddings for a sequence of labels → [N, embedDim]."""
    if not labels:
        return torch.empty(0, embedDim, dtype=torch.float32)
    return torch.stack([labelToEmbedding(label, embedDim) for label in labels], dim=0)


# ==================================================================================
class VocabularyItem(Serializable):
    """One discrete vocabulary entry (e.g. an action key or an argument kind).

    Persists label + description. Converts itself to an embedding tensor on demand.
    """

    def __init__(
        self,
        label: str = "",
        description: str = "",
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()
        self._label: str = label if label is not None else ""
        self._description: str = description if description is not None else ""
        self._embedDim: int = int(embedDim)
        self.Properties.extend(["label", "description", "embedDim"])

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value if value is not None else ""

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value if value is not None else ""

    @property
    def embedDim(self) -> int:
        return self._embedDim

    @embedDim.setter
    def embedDim(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("embedDim must be >= 1")
        self._embedDim = int(value)

    def toEmbedding(self) -> Tensor:
        """Convert this item to a unit embedding vector of shape [embedDim]."""
        if not self._label:
            raise ValueError("VocabularyItem.label must be non-empty to embed")
        return labelToEmbedding(self._label, self._embedDim)


# ==================================================================================
class Vocabulary(Serializable):
    """Ordered finite set of discrete vocabulary items.

    Used for action types and argument kinds only — not for open-ended
    argument values (coordinates, free text, arbitrary key codes).
    """

    def __init__(
        self,
        items: Sequence[VocabularyItem] | None = None,
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> None:
        super().__init__()
        self._items: list[VocabularyItem] = list(items) if items is not None else []
        self._embedDim: int = int(embedDim)
        self.Properties.extend(["items", "embedDim"])
        self._syncEmbedDim()

    def _syncEmbedDim(self) -> None:
        for item in self._items:
            item.embedDim = self._embedDim

    # ------------------------------------------------------------------
    @property
    def items(self) -> tuple[VocabularyItem, ...]:
        return tuple(self._items)

    @items.setter
    def items(self, value: Sequence[VocabularyItem]) -> None:
        self._items = list(value) if value is not None else []
        self._syncEmbedDim()

    @property
    def embedDim(self) -> int:
        return self._embedDim

    @embedDim.setter
    def embedDim(self, value: int) -> None:
        if int(value) < 1:
            raise ValueError("embedDim must be >= 1")
        self._embedDim = int(value)
        self._syncEmbedDim()

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(item.label for item in self._items)

    @property
    def size(self) -> int:
        return len(self._items)

    def toEmbeddings(self) -> Tensor:
        """Convert the whole vocabulary to a tensor of shape [N, embedDim]."""
        if not self._items:
            return torch.empty(0, self._embedDim, dtype=torch.float32)
        return torch.stack([item.toEmbedding() for item in self._items], dim=0)

    @classmethod
    def fromLabels(
        cls,
        labels: Sequence[str],
        descriptions: Sequence[str] | None = None,
        embedDim: int = C_DEFAULT_EMBED_DIM,
    ) -> Vocabulary:
        descriptions = list(descriptions) if descriptions is not None else []
        items: list[VocabularyItem] = []
        for index, label in enumerate(labels):
            description = descriptions[index] if index < len(descriptions) else ""
            items.append(
                VocabularyItem(label=label, description=description, embedDim=embedDim)
            )
        return cls(items=items, embedDim=embedDim)
