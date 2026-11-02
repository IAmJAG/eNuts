# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, Optional

# ==================================================================================
from torch import Tensor
from torch import cat as torchCat
from torch import device as torchDevice

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.policy.vocabulary import iVocabularyItem
from ...utilities import deterministicEmbedding, getTorchDevice


# ==================================================================================
class VocabularyItem(iVocabularyItem, Serializable):
    def __init__(
        self,
        id: str,
        description: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self._id: str = id if id is not None else ""
        self._description: str = description if description is not None else ""
        self._options: Optional[Dict[str, Any]] = options if options is not None else {}
        self.Properties.extend(["id", "description", "options"])

    @property
    def id(self) -> str:
        return self._id

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value if value is not None else ""

    @property
    def options(self) -> Dict[str, Any]:
        return self._options

    @options.setter
    def options(self, value: Dict[str, Any]) -> None:
        self._options = value

    def __copy__(self):
        return VocabularyItem(self._id, self._description, self._options)

    def copy(self):
        return self.__copy__()

    def toTensor(self, dimension: int, fuse: bool = False, device: Optional[str | torchDevice] = "cuda"):
        device: torchDevice = getTorchDevice(device)

        embId: Tensor = deterministicEmbedding(self._id, dimension, device)
        if not fuse: return embId

        options: Dict[str, Any] = self._options or {}
        embOptions: Tensor = deterministicEmbedding(options, dimension, device)

        return torchCat([embId, embOptions], dim=0).to(device)
        

    