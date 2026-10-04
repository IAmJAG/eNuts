# ==================================================================================
# fluxCore/emitters/scrcpy/__SCRCPYEmitter.py
# ==================================================================================
import os

# ==================================================================================
from asyncio import AbstractEventLoop, get_running_loop
from socket import socket

# ==================================================================================
from adbutils import AdbConnection, AdbDevice, adb
from av import InvalidDataError, VideoCodecContext

# ==================================================================================
from jAGFx.services import AsyncService

# ==================================================================================
from ...devices import SCRCPY
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
C_LOG_EVERY_N: int = 30
# ==================================================================================


# ==================================================================================
class SCRCPYEmitter(AsyncService, SCRCPY):
    """Async video/control emitter. Satisfies iSCRCPYEmitter structurally."""

    def __init__(self, serial: str, name: str | None = None) -> None:
        verbose(f"SCRCPYEmitter.__init__: serial={serial!r} name={name!r}")
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncService.__init__(self, work=self.work, name=name)
        self._vSocket: iVideoSocket | None = None
        self._cSocket: iControlSocket | None = None
        self._streamServer: AdbConnection | None = None
        self._codecContext: VideoCodecContext | None = None
        self._frameCount: int = 0
        verbose(f"SCRCPYEmitter.__init__: done id={self.id!r}")

    async def work(self, *args, **kwargs):
        try:
            sckt: iVideoSocket | None = self._vSocket
            if sckt is None:
                await asyncWait(0.05)
                return

            frame: iFrame = await sckt.asyncReceiveSingleFrame()
            self._frameCount += 1

            lLog = (
                frame.isConfig
                or frame.isKeyFrame
                or (self._frameCount % C_LOG_EVERY_N == 0)
            )
            if lLog:
                verbose(
                    f"SCRCPYEmitter.work: packet #{self._frameCount} "
                    f"pts={frame.pts} isConfig={frame.isConfig} isKeyFrame={frame.isKeyFrame} "
                    f"payloadBytes={len(frame.payload)}"
                )

            self.raiseEvent("ON_FRAME", frame)

            # Cooperate with Qt / other tasks when many frames are already buffered
            await asyncWait(0)

        except InvalidDataError as ex:
            verbose(f"SCRCPYEmitter.work: InvalidDataError (ignored) {ex}")
            await asyncWait(0)

        except ConnectionError as ex:
            warning(f"SCRCPYEmitter.work: ConnectionError {ex}")
            raise

        except Exception as ex:
            error(f"SCRCPYEmitter.work: {type(ex).__name__}: {ex}")
            raise

    async def _updateMetadata(self, sckt: iVideoSocket) -> None:
        verbose("SCRCPYEmitter._updateMetadata: reading deviceName (64 bytes)")
        deviceName: bytes = await sckt.receive(64)
        verbose(
            f"SCRCPYEmitter._updateMetadata: raw deviceName len={len(deviceName)} head={deviceName[:8]!r}"
        )

        if deviceName and deviceName[0] == 0x00:
            verbose("SCRCPYEmitter._updateMetadata: leading 0x00 — reading extra byte")
            deviceName = deviceName[1:] + await sckt.receive(1)

        verbose("SCRCPYEmitter._updateMetadata: reading codecId (4 bytes)")
        codecIdRaw: bytes = await sckt.receive(4)
        verbose("SCRCPYEmitter._updateMetadata: reading width (4 bytes)")
        widthRaw: bytes = await sckt.receive(4)
        verbose("SCRCPYEmitter._updateMetadata: reading height (4 bytes)")
        heightRaw: bytes = await sckt.receive(4)

        lCodecId: str = codecIdRaw.decode("ascii", errors="replace").strip("\x00") or "h264"
        lWidth: int = int.from_bytes(widthRaw, "big")
        lHeight: int = int.from_bytes(heightRaw, "big")
        lName: str = deviceName.split(b"\x00", 1)[0].decode("utf-8", errors="replace")

        verbose(
            f"SCRCPYEmitter._updateMetadata: name={lName!r} codecId={lCodecId!r} "
            f"width={lWidth} height={lHeight}"
        )
        self._name = lName
        self.update(codecId=lCodecId, width=lWidth, height=lHeight)
        verbose("SCRCPYEmitter._updateMetadata: update() applied")

    async def initialize(self, GPUID: int = 0, GPUReady: bool = True) -> None:
        verbose(
            f"SCRCPYEmitter.initialize: start serial={self.id!r} "
            f"GPUID={GPUID} GPUReady={GPUReady}"
        )
        verbose(f"SCRCPYEmitter.initialize: SERVER_PATH={SERVER_PATH!r}")

        device: AdbDevice = adb.device(serial=self.id)
        verbose(f"SCRCPYEmitter.initialize: AdbDevice resolved serial={self.id!r}")

        cfg: SCRCPYServerConfig = SCRCPYServerConfig(
            androidPath=ANDROID_PATH,
            jarName=JAR_NAME,
            maxSize=MAX_SIZE,
            maxFps=MAX_FPS,
            bitrate=BITRATE,
        )
        verbose(
            f"SCRCPYEmitter.initialize: SCRCPYServerConfig scid={cfg.Scid:#010x} "
            f"maxSize={cfg.MaxSize} maxFps={cfg.MaxFps} bitrate={cfg.Bitrate} "
            f"control={cfg.Control}"
        )

        verbose("SCRCPYEmitter.initialize: deployServer ...")
        streamServer: AdbConnection = deployServer(
            device, cfg=cfg, serverPath=SERVER_PATH, timeout=3000
        )
        if streamServer is None:
            warning("SCRCPYEmitter.initialize: Failed to deploy scrcpy server")
            return

        verbose("SCRCPYEmitter.initialize: deployServer ok")
        asyncLoop: AbstractEventLoop = get_running_loop()
        verbose(f"SCRCPYEmitter.initialize: event loop={asyncLoop!r}")

        # scrcpy accepts video first, then control; only then sends device metadata
        verbose(f"SCRCPYEmitter.initialize: getSCRCPYADBSocket video scid={cfg.Scid:#010x}")
        vSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)
        verbose(f"SCRCPYEmitter.initialize: video socket obtained {vSCKT!r}")
        self._vSocket = VideoSocket(vSCKT, loop=asyncLoop)
        verbose("SCRCPYEmitter.initialize: VideoSocket wrapped")

        verbose(f"SCRCPYEmitter.initialize: getSCRCPYADBSocket control scid={cfg.Scid:#010x}")
        cSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)
        verbose(f"SCRCPYEmitter.initialize: control socket obtained {cSCKT!r}")
        self._cSocket = ControlSocket(cSCKT, loop=asyncLoop)
        verbose("SCRCPYEmitter.initialize: ControlSocket wrapped")

        await self._updateMetadata(self._vSocket)
        verbose(
            f"SCRCPYEmitter.initialize: metadata ready name={self.name!r} "
            f"codecId={self.codecId!r} {self.width}x{self.height}"
        )

        verbose(
            f"SCRCPYEmitter.initialize: createCodecContext codecId={self.codecId!r} "
            f"GPUID={GPUID} GPUReady={GPUReady}"
        )
        codecCTX: VideoCodecContext = createCodecContext(
            self.codecId, GPUID=GPUID, GPUReady=GPUReady
        )
        verbose(f"SCRCPYEmitter.initialize: codec context {codecCTX!r}")

        self._streamServer = streamServer
        self._codecContext = codecCTX
        self._frameCount = 0
        verbose("SCRCPYEmitter.initialize: complete — ready to receive packets")

    async def emitter(self):
        verbose("SCRCPYEmitter.emitter: stub (not used yet)")
