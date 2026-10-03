# ==================================================================================
# src/fluxCore/types/interface/sockets/__videoSocket.py
# ==================================================================================
from socket import socket
from struct import unpack

# ==================================================================================
from ...types.interface.packets import iFrame
from ...utilities import AsyncReadSingleFrame, ReadSingleFrame
from ..interface.sockets import iVideoSocket
from ..packets.__frame import Frame
from .__socket import SocketBase


# ==================================================================================
class VideoSocket(SocketBase, iVideoSocket):
    async def asyncReceiveSingleFrame(self) -> iFrame:
        try:
            lResult = await AsyncReadSingleFrame(self._socket, self._loop)

        except Exception as e:
            raise e
    
        if lResult is None: raise ConnectionError("Video stream closed or broken")
        lPts, lIsConfig, lIsKeyFrame, lPayload = lResult
        return Frame(lPayload, lPts, lIsConfig, lIsKeyFrame)
    
    def receiveSingleFrame(self) -> iFrame:
        try:
            lResult = ReadSingleFrame(self._socket)

        except Exception as e:
            raise e

        if lResult is None: raise ConnectionError("Video stream closed or broken")
        lPts, lIsConfig, lIsKeyFrame, lPayload = lResult
        return Frame(lPayload, lPts, lIsConfig, lIsKeyFrame)
        