# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, List, Optional, Set, Union, overload

# ==================================================================================
from torch import Tensor
from torch import device as torchDevice
from torch import stack as torchStack

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.policy.vocabulary import iVocabulary, iVocabularyItem
from ...utilities import G_DEFAULT_EMBED_DIM, getTorchDevice
from .__vocabularyItem import VocabularyItem


# ==================================================================================
class Vocabulary[T: iVocabularyItem](iVocabulary, Serializable):
    def __init__(
        self,
        vocabulary: Optional[List[T]] = None, dimension: int = G_DEFAULT_EMBED_DIM,
        fuse: bool = False, device: Optional[str | torchDevice] = None,
    ) -> None:
        super().__init__()

        if dimension < 1:
            raise ValueError("dimension (embed width) must be >= 1")
        
        self._dimension: int = int(dimension)
        self._fuse: bool = fuse
        self._device: torchDevice = getTorchDevice(device)        
        self._vocabulary: List[T] = list(vocabulary or [])

        self._ids: List[str] = list[str]()
        self._embeddings: Tensor = None
        self.Properties.extend(["dimension", "vocabulary", "fuse"])

        self._rebuildEmbedding()

    def _rebuildEmbedding(self):
        if not self._vocabulary: 
            self._ids = []
            self._embeddings = None
            return
        
        dimension: int = self._dimension
        fuse: bool = self._fuse
        device: torchDevice = self._device

        ids: List[str] = [v.id for v in self._vocabulary]
        embeddings: Tensor = torchStack(
            [v.toTensor(dimension=dimension, fuse=fuse, device=device) for v in self._vocabulary], dim=0
        )        
        self._embeddings = embeddings
        self._ids = ids

    @overload
    def add(self, id: str, description: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> None: ...
    @overload
    def add(self, item: T) -> None: ...

    def add(
        self, idItem: Union[str, T], description: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        if isinstance(idItem, str):
            item = VocabularyItem(id=idItem, description=description, options=options)

        else:            
            item = idItem

        self._vocabulary.append(item)
        self._rebuildEmbedding()

    @overload
    def remove(self, id: str) -> None: ...    
    @overload
    def remove(self, item: T) -> None: ...

    def remove(self, idItem: Union[str, T]) -> None:
        id: str = idItem.id if isinstance(idItem, T) else idItem
        self._vocabulary = [v for v in self._vocabulary if v.id != id]
        self._rebuildEmbedding()

    @property
    def embeddings(self) -> Tensor:
        return self._embeddings

    @property
    def ids(self) -> Set[str]:
        return set(self._ids)

    @property
    def vocabulary(self) -> Set[T]:
        return set(self._vocabulary)
    
    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def fuse(self) -> bool:
        return self._fuse

    @fuse.setter
    def fuse(self, value: bool) -> None:
        self._fuse = value

    @property
    def size(self) -> int:
        return len(self._vocabulary)

    @property
    def device(self) -> torchDevice:
        return self._device