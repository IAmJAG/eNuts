# ==================================================================================
from __future__ import annotations

# ==================================================================================
from jAGFx.serializer import Serializable


# ==================================================================================
class ScrcpyInitParams(Serializable):
    """Parameters for ScrcpyInitializeMessage (main → client)."""

    def __init__(
        self,
        serial: str = "",
        gpuId: int = 0,
        gpuReady: bool = False,
    ) -> None:
        super().__init__()
        self._serial: str = serial
        self._gpuId: int = gpuId
        self._gpuReady: bool = gpuReady
        self.Properties.extend(["serial", "gpuId", "gpuReady"])

    @property
    def serial(self) -> str:
        return self._serial

    @property
    def gpuId(self) -> int:
        return self._gpuId

    @property
    def gpuReady(self) -> bool:
        return self._gpuReady


# ==================================================================================
__all__ = ["ScrcpyInitParams"]
