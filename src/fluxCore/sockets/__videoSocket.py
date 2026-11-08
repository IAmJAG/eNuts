# ==================================================================================
from ..packets import SCRCPYPacket
from ..types.interface.packets import iImagePacket
from ..types.interface.sockets import iVideoSocket
from ..utilities import AsyncReadSingleFrame, ReadSingleFrame
from .__socket import SocketBase


# ==================================================================================
class VideoSocket[T: iImagePacket](SocketBase, iVideoSocket):
    async def asyncReceiveSingleFrame(self) -> T:
        lResult = await AsyncReadSingleFrame(self._socket, self._loop)
        if lResult is None:
            raise ConnectionError("Video stream closed or broken")
        # AsyncReadSingleFrame → (pts, isConfig, isKeyFrame, payload)
        pts, isConfig, isKeyFrame, payload = lResult
        return T(payload, pts, isConfig, isKeyFrame)

    def receiveSingleFrame(self) -> T:
        lResult = ReadSingleFrame(self._socket)
        if lResult is None:
            raise ConnectionError("Video stream closed or broken")
        # ReadSingleFrame → (pts, isConfig, isKeyFrame, payload)
        pts, isConfig, isKeyFrame, payload = lResult
        return T(payload, pts, isConfig, isKeyFrame)
