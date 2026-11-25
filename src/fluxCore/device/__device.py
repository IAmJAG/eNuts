# ==================================================================================
from typing import Optional, Union
from uuid import UUID, uuid4

# ==================================================================================
from jAGFx.serializer import Serializable

# ==================================================================================
from ..types.interface.device import iDevice


# ==================================================================================
class Device(Serializable, iDevice):
    def __init__(
        self, ident: Optional[Union[str, UUID]] = None, 
        name: Optional[str] = None,
        width: Optional[int] = None, height: Optional[int] = None
    ) -> None:
        super().__init__()
        self._id: Union[str, UUID] = ident or uuid4()
        self._name: Optional[str] = name 
        self._width: int = width    
        self._height: int = height

        self.Properties.extend(["id", "name", "width", "height"])

    def updateInfo(self): 
        warning("updateInfo not implemented.")       

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> Optional[str]:
        if self._name is None: 
            self.updateInfo()
        return self._name

    @property
    def width(self) -> int: 
        if self._width is None: 
            self.updateInfo()

        return self._width
    
    @property
    def height(self) -> int: 
        if self._height is None: 
            self.updateInfo()
        return self._height