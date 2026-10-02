# ==================================================================================
# src/fluxCore/types/interface/sockets/__videoSocket.py
# ==================================================================================
from socket import socket
from struct import unpack

# ==================================================================================
from ...types.interface.sockets import iFrame, iVideoSocket
from ...utilities import ReadExact
from ..sockets import iFrame
from .__frame import Frame
from .__socket import SocketBase


# ==================================================================================
class VideoSocket(SocketBase, iVideoSocket):    
    def receiveSingleFrame(self) -> iFrame:
        try:
            sckt: socket = self._socket
            lHeaderBytes: bytes = ReadExact(self._socket, 12)
            if len(lHeaderBytes) < 12:
                raise ConnectionError("Video stream is closed or broken.")

            # Unpack as big-endian: 64-bit int (PTS + flags) and 32-bit int (payload size)
            lHeaderVal, lPayloadSize = unpack(">QI", lHeaderBytes)

            # Extract metadata flags and PTS from the 64-bit value
            lIsConfig = (lHeaderVal & 0x8000000000000000) != 0
            lIsKeyFrame = (lHeaderVal & 0x4000000000000000) != 0
            lPts = lHeaderVal & 0x3FFFFFFFFFFFFFFF

            lPayload = b""
            if lPayloadSize > 0:
                lPayload = ReadExact(sckt, lPayloadSize)

            frame: iFrame = Frame(
                lPayload,
                lPts,
                lIsConfig,
                lIsKeyFrame
            )
            return frame

        except Exception as e:
            raise e
        