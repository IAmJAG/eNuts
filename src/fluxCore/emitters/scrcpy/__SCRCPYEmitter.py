# ==================================================================================
# src/fluxCore/emitters/scrcpy/__SCRCPYEmitter.py
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
MAX_SIZE = 3200
MAX_FPS = 120
BITRATE = 16000000
# ==================================================================================


# ==================================================================================
class SCRCPYEmitter(AsyncService, SCRCPY):
    """Async video/control emitter. Satisfies iSCRCPYEmitter structurally."""

    def __init__(self, serial: str, name: str | None = None) -> None:
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncService.__init__(self, work=self.work, name=name)
        self._vSocket: iVideoSocket | None = None
        self._cSocket: iControlSocket | None = None
        self._streamServer: AdbConnection | None = None
        self._codecContext: VideoCodecContext | None = None
        self._serverLogStop: ThreadEvent = ThreadEvent()
        self._serverLogThread: Thread | None = None

    # ==================================================================================
    @property
    def ControlSocket(self) -> iControlSocket | None:
        """Public control-channel accessor. Returns None when unavailable."""
        if not hasattr(self, "_cSocket"):
            return None
        return self._cSocket

    @property
    def CodecContext(self) -> VideoCodecContext | None:
        """Public decoder context for frame consumers (e.g. imageStreamer)."""
        return self._codecContext

    # ==================================================================================
    def _startServerLogDrain(self, streamServer: AdbConnection) -> None:
        """Prevent scrcpy-server from blocking on a full stdout pipe."""

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
        """Drain the video socket continuously until the service is stopped."""
        sckt: iVideoSocket = self._vSocket
        if sckt is None:
            return

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

                # qasync + Windows IOCP: yield so overlapped reads can complete
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

    async def initialize(self, GPUID: int = 0, GPUReady: bool = True) -> None:
        device: AdbDevice = adb.device(serial=self.id)

        cfg: SCRCPYServerConfig = SCRCPYServerConfig(
            androidPath=ANDROID_PATH,
            jarName=JAR_NAME,
            maxSize=MAX_SIZE,
            maxFps=MAX_FPS,
            bitrate=BITRATE,
            logLevel="warn",
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

        await self._updateMetadata(self._vSocket)

        self._codecContext = createCodecContext(
            self.codecId, GPUID=GPUID, GPUReady=GPUReady
        )
