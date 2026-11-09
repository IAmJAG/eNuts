# ==================================================================================================
from jAGFx.serializer import Serializable
from jAGFx.types.interface.configuration import iConfiguration


# ==================================================================================================
class DecodeCapacity(Serializable, iConfiguration):
    C_MINIMUM: int = 4
    C_MAXIMUM: int = 256

    def __init__(self) -> None:
        super().__init__()
        self._minimum: int = self.C_MINIMUM
        self._maximum: int = self.C_MAXIMUM
        self._current: int = self._minimum
        self.Properties.extend(["minimum", "maximum", "current"])

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
        if not isinstance(value, int):
            raise TypeError("Decode queue capacity must be an integer")
        if value < self._minimum or value > self._maximum:
            raise ValueError(
                f"Decode queue capacity must be between {self._minimum} and {self._maximum}"
            )
        self._current = value
