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

    @vramCap.setter
    def vramCap(self, value: float) -> None:
        if not 0.0 < value <= 1.0:
            raise ValueError("VRAM cap must be greater than 0 and at most 1")
        self._vramCap = float(value)
