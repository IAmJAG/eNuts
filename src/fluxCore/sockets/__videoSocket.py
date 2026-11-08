# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import AbstractEventLoop
from socket import socket
from typing import Type

# ==================================================================================
from ..packets import TensorPacket
from ..types.interface.packets import iImagePacket
from ..types.interface.sockets import iVideoSocket
from ..utilities import AsyncReadSingleFrame, ReadSingleFrame
from .__socket import SocketBase


# ==================================================================================
class VideoSocket(SocketBase, iVideoSocket):
    """Video frame socket. ``packetType`` is the concrete ``iImagePacket`` class
    used to build frames (PEP 695 TypeVars are not callable at runtime).
    """

    def __init__(
        self,
        sckt: socket,
        loop: AbstractEventLoop | None = None,
        packetType: Type[iImagePacket] = TensorPacket,
    ) -> None:
        super().__init__(sckt, loop)
        self._packetType: Type[iImagePacket] = packetType

    async def asyncReceiveSingleFrame(self) -> iImagePacket:
        lResult = await AsyncReadSingleFrame(self._socket, self._loop)
        if lResult is None:
            raise ConnectionError("Video stream closed or broken")
        pts, isConfig, isKeyFrame, payload = lResult
        return self._packetType(payload, pts, isConfig, isKeyFrame)

    def receiveSingleFrame(self) -> iImagePacket:
        lResult = ReadSingleFrame(self._socket)
        if lResult is None:
            raise ConnectionError("Video stream closed or broken")
        pts, isConfig, isKeyFrame, payload = lResult
        return self._packetType(payload, pts, isConfig, isKeyFrame)
