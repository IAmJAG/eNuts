# ==================================================================================
# src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py
# ==================================================================================
import os

# ==================================================================================
from asyncio import AbstractEventLoop, CancelledError, Task, get_running_loop
from socket import socket
from threading import Event as ThreadEvent
from threading import Thread

# ==================================================================================
from adbutils import AdbConnection, AdbDevice, adb
from av import InvalidDataError, VideoCodecContext

# ==================================================================================
from jAGFx.services import AsyncService
from utilities import createTask

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
MAX_SIZE = 1920
MAX_FPS = 60
BITRATE = 4000000
# ==================================================================================

# ==================================================================================
class SCRCPYEmitter(AsyncService, SCRCPY):
    def __init__(self, serial: str, name: str | None = None) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)        
        AsyncService.__init__(self, work=self.work, name=self.name)
        self._vSocket: iVideoSocket | None = None
        self._cSocket: iControlSocket | None = None
        self._streamServer: AdbConnection | None = None
        self._codecContext: VideoCodecContext | None = None
        self._serverLogStop: ThreadEvent = ThreadEvent()
        self._serverLogThread: Thread | None = None

    # ==================================================================================
    @property
    def ControlSocket(self) -> iControlSocket | None:
        if not hasattr(self, "_cSocket"): return None
        return self._cSocket

    # ==================================================================================
    def _startServerLogDrain(self, streamServer: AdbConnection) -> None:
        def _drain() -> None:
            try:
                while not self._serverLogStop.is_set():
                    try:
                        lChunk = streamServer.read(4096)

                    except Exception:
                        break

                    if not lChunk: break

            finally:
                pass

        self._serverLogStop.clear()
        self._serverLogThread = Thread(target=_drain, name=f"scrcpy-log-{self.id}", daemon=True)
        self._serverLogThread.start()

    def _stopServerLogDrain(self) -> None:
        self._serverLogStop.set()
        lThread = self._serverLogThread
        if lThread is not None and lThread.is_alive():
            lThread.join(timeout=1.0)
        self._serverLogThread = None

    async def work(self, *args, **kwargs):
        sckt: iVideoSocket = self._vSocket
        if sckt is None: return

        try:
            while self.isRunning:
                try:
                    frame: iFrame = await sckt.asyncReceiveSingleFrame()
                    self.raiseEvent("ON_FRAME", frame)

                except CancelledError:
                    raise

                except InvalidDataError:
                    await asyncWait(0)
                    continue

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

    def initialize(self, GPUID: int = 0, GPUReady: bool = True) -> None:
        device: AdbDevice = adb.device(serial=self.id)

        cfg: SCRCPYServerConfig = SCRCPYServerConfig(
            androidPath=ANDROID_PATH, jarName=JAR_NAME, maxSize=MAX_SIZE,
            maxFps=MAX_FPS, bitrate=BITRATE, logLevel="warn",
        )

        streamServer: AdbConnection = deployServer(
            device, cfg=cfg, serverPath=SERVER_PATH, timeout=3000
        )
        if streamServer is None:
            raise RuntimeError("Failed to deploy scrcpy server")

        self._streamServer = streamServer
        self._startServerLogDrain(streamServer)

        asyncLoop: AbstractEventLoop = get_running_loop()

        # scrcpy accepts video first, then control; only then sends device metadata
        vSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)
        self._vSocket = VideoSocket(vSCKT, loop=asyncLoop)

        cSCKT: socket = getSCRCPYADBSocket(device, scid=cfg.Scid, timeout=3000)
        self._cSocket = ControlSocket(cSCKT, loop=asyncLoop)

        task: Task = createTask(self._updateMetadata, self._vSocket)

        def _onMetadataDone(fut: Task) -> None:
            try:
                fut.result()  # re-raise if _updateMetadata failed
            except Exception as ex:
                error(f"[{self.__class__.__name__}] metadata update failed", ex)
                return

            # codecId is now correct (written by _updateMetadata → self.update)
            self._codecContext = createCodecContext(
                self.codecId, GPUID=GPUID, GPUReady=GPUReady
            )

        task.add_done_callback(_onMetadataDone)
