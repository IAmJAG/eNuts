# ==================================================================================
from typing import Optional, Union
from uuid import UUID

# ==================================================================================
from adbutils import AdbDevice, adb

# ==================================================================================
from .__device import Device


# ==================================================================================
class SCRCPYDevice(Device):
    def __init__(
        self, ident: Optional[Union[str, UUID]] = None, 
        name: Optional[str] = None,
        width: Optional[int] = None, height: Optional[int] = None
    ) -> None:
        super().__init__(ident=ident, name=name, width=width, height=height)

    def updateInfo(self):
        serial: str = self._id
        
        device: AdbDevice = adb.device(serial)
        self._width, self._height = device.window_size()

        model: str = adb.shell(serial, "getprop ro.product.model")
        manufacturer: str = adb.shell(serial, "getprop ro.product.manufacturer")

        self._name = f"{manufacturer}:{model}"

