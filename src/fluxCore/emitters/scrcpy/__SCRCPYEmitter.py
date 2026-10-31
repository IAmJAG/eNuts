# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os

# ==================================================================================
from asyncio import AbstractEventLoop, CancelledError, get_running_loop
from socket import socket
from threading import Event as ThreadEvent
from threading import Thread

# ==================================================================================
from adbutils import AdbConnection, AdbDevice, adb
from av import InvalidDataError, VideoCodecContext

# ==================================================================================
from jAGFx.services import AsyncService
from jAGFx.services.__subscription import AsyncSubscription

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
from .__footprint import SCRCPYError

# ==================================================================================
JAR_NAME = "scrcpy-server.jar"
SERVER_PATH = os.path.join(os.getcwd(), ".bin", JAR_NAME)
ANDROID_PATH = "/data/local/tmp/"
MAX_SIZE = 1920
MAX_FPS = 60
BITRATE = 4000000
# ==================================================================================


# ==================================================================================
class SCRCPYEmitter(AsyncService, SCRCPY):
    """Async video/control emitter. Satisfies iSCRCPYEmitter structurally.

    Events never pass the emitter instance:
    - ON_METADATA_UPDATE → base SCRCPY via toScrcpy
    - ON_FRAME → iFrame (in-process only)
    - ON_ERROR → SCRCPYError
    plus AsyncService lifecycle events (no args).

    All SCRCPYEmitter-raised events use asyncRaiseEvent (same as AsyncSubscription).
    """

    def __init__(self, serial: str, name: str | None = None) -> None:
        # AsyncService first so AsyncSubscription._callbacks exists before any raiseEvent.
        # SCRCPY second for device identity / codec metadata fields.
        AsyncService.__init__(self, work=self.work, name=name)
        SCRCPY.__init__(self, serial=serial, name=name)
        if not hasattr(self, "_callbacks"):
            AsyncSubscription.__init__(self)
        self._vSocket: iVideoSocket | None = None
        self._cSocket: iControlSocket | None = None
        self._streamServer: AdbConnection | None = None
        self._codecContext: VideoCodecContext | None = None
        self._serverLogStop: ThreadEvent = ThreadEvent()
        self._serverLogThread: Thread | None = None

    @classmethod
    def toScrcpy(cls, emitter: SCRCPYEmitter) -> SCRCPY:
        scrcpy = SCRCPY(serial=str(emitter.id), name=emitter.name)
        scrcpy.update(
            codecId=emitter.codecId,
            width=emitter.width,
            height=emitter.height,
        )
        return scrcpy

    @property
    def ControlSocket(self) -> iControlSocket | None:
        if not hasattr(self, "_cSocket"):
            return None
        return self._cSocket

    async def _raiseError(self, phase: str, message: str) -> None:
        await self.asyncRaiseEvent(
            "ON_ERROR",
            SCRCPYError(phase=phase, message=message, serial=str(self.id)),
        )

    def _startServerLogDrain(self, streamServer: AdbConnection) -> None:
        def _drain() -> None:
            try:
                while not self._serverLogStop.is_set():
                    try:
                        lChunk = streamServer.read(4096)
                    except Exception:
                        break
                    if not lChunk:
                        break
            finally:
                pass

        self._serverLogStop.clear()
        self._serverLogThread = Thread(
            target=_drain, name=f"scrcpy-log-{self.id}", daemon=True
        )
        self._serverLogThread.start()

    def _stopServerLogDrain(self) -> None:
        self._serverLogStop.set()
        lThread = self._serverLogThread
        if lThread is not None and lThread.is_alive():
            lThread.join(timeout=1.0)
        self._serverLogThread = None

    async def work(self, *args, **kwargs):
        sckt: iVideoSocket = self._vSocket
        if sckt is None:
            return
        try:
            while self.isRunning:
                try:
                    frame: iFrame = await sckt.asyncReceiveSingleFrame()
                    await self.asyncRaiseEvent("ON_FRAME", frame)
                except CancelledError:
                    raise
                except InvalidDataError:
                    await asyncWait(0)
                    continue
                except Exception as ex:
                    await self._raiseError("work", str(ex))
                    raise
                await asyncWait(0)
        finally:
            self._stopServerLogDrain()

    async def _updateMetadata(self, sckt: iVideoSocket) -> None:
        deviceName: bytes = await sckt.receive(64)
        if deviceName and deviceName[0] == 0x00:
            deviceName = deviceName[1:] + await sckt.receive(1)
        codecIdRaw: bytes = await sckt.receive(4)
        widthRaw: bytes = await sckt.receive(4)
        heightRaw: bytes = await sckt.receive(4)
        lCodecId: str = (
            codecIdRaw.decode("ascii", errors="replace").strip("\x00") or "h264"
        )
        lWidth: int = int.from_bytes(widthRaw, "big")
        lHeight: int = int.from_bytes(heightRaw, "big")
        lName: str = deviceName.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
        self._name = lName
        self.update(codecId=lCodecId, width=lWidth, height=lHeight)
        me: SCRCPY = self.toScrcpy(self)
        await self.asyncRaiseEvent("ON_METADATA_UPDATE", me)

    async def initialize(self, GPUID: int = 0, GPUReady: bool = False) -> None:
        """Deploy scrcpy server and open sockets. Default SW decode (GPUReady=False)."""
        self.setSuppressEvent(True)
        device: AdbDevice = adb.device(serial=self.id)
        cfg: SCRCPYServerConfig = SCRCPYServerConfig(
            androidPath=ANDROID_PATH,
            jarName=JAR_NAME,
            maxSize=MAX_SIZE,
            maxFps=MAX_FPS,
            bitrate=BITRATE,
            logLevel="warn",
        )
        try:
            streamServer: AdbConnection = deployServer(
                device, cfg=cfg, serverPath=SERVER_PATH, timeout=3000
            )
        except Exception as ex:
            await self._raiseError("initialize.deploy", str(ex))
            raise
        if streamServer is None:
            await self._raiseError(
                "initialize.deploy", "Failed to deploy scrcpy server"
            )
            raise RuntimeError("Failed to deploy scrcpy server")
        self._streamServer = streamServer
        self._startServerLogDrain(streamServer)
        asyncLoop: AbstractEventLoop = get_running_loop()
        try:
            vSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)
            self._vSocket = VideoSocket(vSCKT, loop=asyncLoop)
            cSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)
            self._cSocket = ControlSocket(cSCKT, loop=asyncLoop)
        except Exception as ex:
            await self._raiseError("initialize.socket", str(ex))
            raise
        try:
            await self._updateMetadata(self._vSocket)
        except Exception as ex:
            await self._raiseError("initialize.metadata", str(ex))
            raise
        try:
            self._codecContext = createCodecContext(
                self.codecId, GPUID=GPUID, GPUReady=GPUReady
            )
            await self.asyncRaiseEvent("ON_INITIALIZED", self._codecContext)
        except Exception as ex:
            await self._raiseError("initialize.codec", str(ex))
            raise
        # Re-enable events so ON_FRAME reaches LocalDeviceStream subscribers.
        self.setSuppressEvent(False)
