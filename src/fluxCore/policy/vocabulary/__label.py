# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ...types.interface.policy.vocabulary import iLabel


# ==================================================================================
class Label(iLabel, Serializable):
    def __init__(self, id: str, description: str) -> None:
        self._id: str = id
        self._description: str = description

    @property
    def id(self) -> str: 
        return self._id
    
    @property
    def description(self) -> str: 
        return self._description
