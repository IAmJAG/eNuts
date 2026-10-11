# ==================================================================================
from ..device import Device

# ==================================================================================
from ..types.interface.devices import iSCRCPY


# ==================================================================================
class SCRCPY(Device, iSCRCPY):
    def __init__(self, serial: str, name: str | None = None, manufacturer: str | None = None) -> None:        
        super().__init__(ident=serial, name=name)
        self._manufacturer: str = manufacturer

    @property
    def serial(self) -> str:
        return super().id

    @property
    def model(self) -> str:
        return super().name

    @model.setter
    def model(self, value: str):
        super().name = value

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value: str):
        self._manufacturer = value