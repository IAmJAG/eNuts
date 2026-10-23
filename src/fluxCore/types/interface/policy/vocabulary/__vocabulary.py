# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import List, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable


# ==================================================================================
@runtime_checkable
class iVocabulary(iSerializable, Protocol):
    @property
    def dimension(self) -> int: ...
    @property
    def size(self) -> int: ...
    @property
    def labels(self) -> List[str]: ...
    def toTensor(self) -> Tensor: ...
