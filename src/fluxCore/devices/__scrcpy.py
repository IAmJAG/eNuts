# ==================================================================================
# src/fluxCore/types/interface/__scrcpy.py
# ==================================================================================
from ..device import Device

# ==================================================================================
from ..types.interface.devices import iSCRCPY


# ==================================================================================
class SCRCPY(Device, iSCRCPY):
    def __init__(self, serial: str, name: str | None = None) -> None:        
        super().__init__(serial, name)
        self._codecId: str = "h264"
        self._width: int = 0
        self._height: int = 0

    @property
    def serial(self) -> str | None:
        return self.id

    @property
    def codecId(self) -> str:
        return self._codecId
    
    @property
    def width(self) -> int: 
        return self._width
    
    @property
    def height(self) -> int: 
        return self._height

    def update(self, codecId: str, width: int, height: int) -> None:
        self._codecId = codecId
        self._width = width
        self._height = height