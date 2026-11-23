# ==================================================================================
from typing import Optional, Union
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.names import getRandomName
from jAGFx.serializer import Serializable

# ==================================================================================
from ..types.interface.device import iDevice


# ==================================================================================
class Device(Serializable, iDevice):
    def __init__(
        self, ident: Optional[Union[str, UUID]] = None, 
        name: Optional[str] = None,
        width: int = 0, height: int = 0
    ) -> None:
        super().__init__()
        self._id = ident or uuid4()
        self._name = name or getRandomName() 
        self._width: int = width    
        self._height: int = height

        self.Properties.extend(["id", "name", "width", "height"])

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def width(self) -> int: 
        return self._width
    
    @property
    def height(self) -> int: 
        return self._height