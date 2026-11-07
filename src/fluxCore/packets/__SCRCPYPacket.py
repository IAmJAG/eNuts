# ==================================================================================
from .__packet import Packet


# ==================================================================================
class SCRCPYPacket(Packet):
    def __init__(self, data: bytes, pts: int, isConfig: bool, isKeyFrame: bool):
        super().__init__(data)
        self._isKeyFrame: bool = isKeyFrame
        self._isConfig: bool = isConfig
        self._pts: int = pts

    @property
    def isKeyFrame(self) -> bool:
        return self._isKeyFrame

    @isKeyFrame.setter
    def isKeyFrame(self, value: bool) -> None:
        self._isKeyFrame = value

    @property
    def isConfig(self) -> bool:
        return self._isConfig

    @isConfig.setter
    def isConfig(self, value: bool) -> None:
        self._isConfig = value

    @property
    def pts(self) -> int:
        return self._pts

    @pts.setter
    def pts(self, value: int) -> None:
        self._pts = value

# ==================================================================================
__all__ = ["SCRCPYPacket"]