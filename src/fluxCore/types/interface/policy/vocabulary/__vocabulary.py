# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import (
    Any,
    Dict,
    Optional,
    Protocol,
    Set,
    Union,
    overload,
    runtime_checkable,
)

# ==================================================================================
from torch import Tensor
from torch import device as torchDevice

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable

# ==================================================================================
from .__vocabularyItem import iVocabularyItem


# ==================================================================================
@runtime_checkable
class iVocabulary[T: iVocabularyItem](iSerializable, Protocol):
    @overload
    def add(self, id: str, description: Optional[str] = None, options: Optional[Dict[str, Any]] = None) -> None: ...
    @overload
    def add(self, item: T) -> None: ...

    def add(self, idItem: Union[str, T], description: Optional[str] = None, options: Optional[Dict[str, Any]] = None,) -> None: ...

    @overload
    def remove(self, id: str) -> None: ...    
    @overload
    def remove(self, item: T) -> None: ...
    def remove(self, idItem: Union[str, T]) -> None: ...

    @property
    def embeddings(self) -> Tensor: ...
    @property
    def ids(self) -> Set[str]: ...
    @property
    def vocabulary(self) -> Set[T]: ...
    @property
    def dimension(self) -> int: ...
    @property
    def fuse(self) -> bool: ...
    @property
    def size(self) -> int: ...
    @property
    def device(self) -> torchDevice: ...