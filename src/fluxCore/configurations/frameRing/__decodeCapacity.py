# ==================================================================================================
from jAGFx.serializer import Serializable
from jAGFx.types.interface.configuration import iConfiguration


# ==================================================================================================
class DecodeCapacity(Serializable, iConfiguration):
    def __init__(self) -> None:
        super().__init__()
        self._minimum: int = 4
        self._maximum: int = 256
        self._current: int = self._minimum
        self.Properties.extend(["minimum", "maximum"])

    @property
    def minimum(self) -> int:
        return self._minimum

    @property
    def maximum(self) -> int:
        return self._maximum

    @property
    def current(self) -> int:
        return self._current

    @current.setter
    def current(self, value: int) -> None:
        self._current = value