# ==================================================================================
from __future__ import annotations

# ==================================================================================
from typing import Dict, List, Protocol, runtime_checkable

# ==================================================================================
from torch import Tensor

# ==================================================================================
from jAGFx.types.interface.serializer import iSerializable

# ==================================================================================
from .__label import iLabel


# ==================================================================================
@runtime_checkable
class iVocabulary(iSerializable, Dict[str, iLabel], Protocol):
    @property
    def dimension(self) -> int: ...
    @property
    def labels(self) -> List[str]: ...
    def toTensor(self) -> Tensor: ...

    
