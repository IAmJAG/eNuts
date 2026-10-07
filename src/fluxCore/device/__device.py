# ==================================================================================
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.names import getRandomName
from jAGFx.serializer import Serializable

# ==================================================================================
from ..types.interface.device import iDevice


# ==================================================================================
class Device(Serializable, iDevice):
    def __init__(self, ident: str | UUID  | None = None, name: str | None = None) -> None: 
        self._id: str = ident or uuid4()
        self._name: str | None = name or getRandomName()
    
    @property 
    def id(self) -> str: 
        return self._id
    
    @property
    def name(self) -> str | None:
        return self._name
    