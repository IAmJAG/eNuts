# ==================================================================================
# fluxCore/emitters/scrcpy/__SCRCPYEmitter.py
# ==================================================================================
import os

# ==================================================================================
from asyncio import AbstractEventLoop, get_running_loop
from socket import socket

# ==================================================================================
from adbutils import AdbConnection, AdbDevice
from av import InvalidDataError, VideoCodecContext

# ==================================================================================
from jAGFx.services import AsyncService, AsyncSubscription

# ==================================================================================
from ...devices import SCRCPY
from ...types.interface.emitters import iSCRCPYEmitter
from ...types.interface.packets import iFrame
from ...types.interface.sockets import iControlSocket, iVideoSocket
from ...types.sockets import ControlSocket, VideoSocket
from ...utilities.scrcpy import (
    SCRCPYServerConfig,
    createCodecContext,
    deployServer,
    getSCRCPYADBSocket,
)

# ==================================================================================
JAR_NAME = "scrcpy-server.jar"
SERVER_PATH = os.path.join(os.getcwd(), ".bin", JAR_NAME)
ANDROID_PATH = "/data/local/tmp/"
MAX_SIZE = 0
MAX_FPS = 0
BITRATE = 4000000
# ==================================================================================


# ==================================================================================
class SCRCPYEmitter(AsyncService, SCRCPY, AsyncSubscription, iSCRCPYEmitter):
    def __init__(self, serial: str, name: str | None = None) -> None:
        AsyncService.__init__(self, work=self.work, name=name)
        SCRCPY.__init__(self, serial=serial, name=name)

    async def work(self, *args, **kwargs):
        try:
            sckt: iVideoSocket = self._vSocket
            if sckt is None:
                return
            frame: iFrame = await sckt.asyncReceiveSingleFrame()
            self.raiseEvent("ON_FRAME", frame)

        except InvalidDataError:
            pass

        except Exception as ex:
            raise ex

    async def _updateMetadata(self, sckt: iVideoSocket):
        deviceName: bytes = await sckt.receive(64)
        if deviceName[0] == 0x00:
            deviceName = deviceName[1:] + await sckt.receive(1)

        codecId: bytes = await sckt.receive(4)
        width: bytes = await sckt.receive(4)
        height: bytes = await sckt.receive(4)

        self._name = deviceName.decode("utf-8", errors="replace")
        self.update(
            codecId=codecId,
            width=int.from_bytes(width, "big"),
            height=int.from_bytes(height, "big"),
        )

    async def initialize(self, GPUID: int = 0, GPUReady: bool = True):
        device: AdbDevice = AdbDevice(serial=self.id)
        cfg: SCRCPYServerConfig = SCRCPYServerConfig(
            androidPath=ANDROID_PATH,
            jarName=JAR_NAME,
            maxSize=MAX_SIZE,
            maxFps=MAX_FPS,
            bitrate=BITRATE,
        )

        streamServer: AdbConnection = deployServer(
            device, cfg=cfg, serverPath=SERVER_PATH, timeout=3000
        )
        if streamServer is None:
            warning("Failed to deploy scrcpy server")
            return

        asyncLoop: AbstractEventLoop = get_running_loop()

        vSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)
        self._vSocket: iVideoSocket = VideoSocket(vSCKT, loop=asyncLoop)
        await self._updateMetadata(self._vSocket)

        codecCTX: VideoCodecContext = createCodecContext(
            self.codecId, GPUID=GPUID, GPUReady=GPUReady
        )
        cSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)

        self._cSocket: iControlSocket = ControlSocket(cSCKT, loop=asyncLoop)
        self._streamServer: AdbConnection = streamServer
        self._codecContext: VideoCodecContext = codecCTX

    async def emitter(self):
        ...
