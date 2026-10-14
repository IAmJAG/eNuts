# ==================================================================================
# src/fluxCore/types/sockets/__videoSocket.py
# ==================================================================================
from ...types.interface.packets import iFrame
from ...utilities import AsyncReadSingleFrame, ReadSingleFrame
from ..interface.sockets import iVideoSocket
from ..packets.__frame import Frame
from .__socket import SocketBase


# ==================================================================================
class VideoSocket(SocketBase, iVideoSocket):
    async def asyncReceiveSingleFrame(self) -> iFrame:
        lResult = await AsyncReadSingleFrame(self._socket, self._loop)
        if lResult is None: raise ConnectionError("Video stream closed or broken")
        lPts, lIsConfig, lIsKeyFrame, lPayload = lResult
        return Frame(lPayload, lPts, lIsConfig, lIsKeyFrame)

    def receiveSingleFrame(self) -> iFrame:
        lResult: tuple[int, bool, bool, bytes] = ReadSingleFrame(self._socket)    
        lPts, lIsConfig, lIsKeyFrame, lPayload = lResult
        return Frame(lPayload, lPts, lIsConfig, lIsKeyFrame)
    
