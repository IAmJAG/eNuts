# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Any, Dict, Optional, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor
from torch import device as torchDevice

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iVocabularyItem(iSerializable, Protocol):    
    @property
    def id(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def options(self) -> Dict[str, Any]: ...  

    def __copy__(self) -> iVocabularyItem: ...

    def copy(self) -> iVocabularyItem: ...
    def toTensor(self, dimension: int, fuse: bool = False, device: Optional[str | torchDevice] = "cuda") -> Tensor: ...