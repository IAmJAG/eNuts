# ==================================================================================================
from jAGFx.serializer import Serializable
from jAGFx.types.interface.configuration import iConfiguration

# ==================================================================================================
from .__decodeCapacity import DecodeCapacity


# ==================================================================================================
class FrameRingConfiguration(Serializable, iConfiguration):    
    def __init__(self) -> None:
        super().__init__()
        self._decodeCapacity: DecodeCapacity = DecodeCapacity()
        self._vramCap: float = 0.85        
        self.Properties.extend(["decodeCapacity", "vramCap"])

    @property
    def decodeCapacity(self) -> DecodeCapacity:
        return self._decodeCapacity

    @property
    def vramCap(self) -> float:
        return self._vramCap

    def setCapacity(self, capacity: int) -> None:
        self._decodeCapacity.current = capacity
