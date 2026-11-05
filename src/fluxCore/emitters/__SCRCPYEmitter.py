# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os

# ==================================================================================
from asyncio import AbstractEventLoop, CancelledError, Task, get_running_loop, to_thread
from socket import socket
from threading import Event as ThreadEvent
from threading import Thread

# ==================================================================================
from typing import Optional

# ==================================================================================
from adbutils import AdbConnection, AdbDevice, adb
from av import InvalidDataError, VideoCodecContext

# ==================================================================================
from jAGFx.services import AsyncService
from jAGFx.services.__subscription import AsyncSubscription

# ==================================================================================
from ..devices import SCRCPY
from ..types.interface.device import iDevice
from ..types.interface.emitters import iSCRCPYEmitter
from ..types.interface.packets import iFrame
from ..types.interface.sockets import iControlSocket, iVideoSocket
from ..types.sockets import ControlSocket, VideoSocket
from ..utilities.scrcpy import (
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
    """
    Async video/control emitter. Satisfies iSCRCPYEmitter structurally.

    Events never pass the emitter instance:
    - ON_METADATA_UPDATE → base SCRCPY via toScrcpy
    - ON_FRAME → iFrame (in-process only)
    - ON_ERROR → SCRCPYError
    plus AsyncService lifecycle events (no args).

    Blocking ADB (deploy / abstract sockets) runs in a worker thread via
    ``asyncio.to_thread`` so the qasync UI loop stays responsive during init.
    """

    def __init__(self, serial: str, name: str | None = None) -> None:
        AsyncService.__init__(self, work=self.work, name=name)
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncSubscription.__init__(self)

        self._vSocket: Optional[iVideoSocket] = None
        self._cSocket: Optional[iControlSocket] = None
        self._streamServer: Optional[AdbConnection] = None
        self._codecContext: Optional[VideoCodecContext] = None
        self._serverLogThread: Optional[Thread] = None
        self._serverLogStop: ThreadEvent = ThreadEvent()

    @classmethod
    def toSCRCPY(cls, emitter: SCRCPYEmitter) -> SCRCPY:
        return cls.toDevice(emitter)

    @classmethod
    def toDevice(self, device: iDevice) -> Optional[iDevice]:
        scrcpy: SCRCPY = SCRCPY(serial=str(device.id), name=device.name)
        scrcpy.update(
            codecId=device.codecId,
            width=device.width,
            height=device.height,
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
            RuntimeError(f"[SCRCPY] {phase}: {message}"),
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

        me: SCRCPY = self.toSCRCPY(self)
        await self.asyncRaiseEvent("ON_METADATA_UPDATE", me)

    async def initialize(self, GPUID: int = 0, GPUReady: bool = False) -> None:
        """Deploy scrcpy server and open sockets. Default SW decode (GPUReady=False).

        Blocking ADB deploy and abstract-socket connect run in ``to_thread`` so the
        UI event loop is not stalled for multi-second sleeps/retries.
        """
        try:
            self.setSuppressEvent(True)

            device: AdbDevice = await to_thread(adb.device, serial=self.id)
            cfg: SCRCPYServerConfig = SCRCPYServerConfig(
                androidPath=ANDROID_PATH,
                jarName=JAR_NAME,
                maxSize=MAX_SIZE,
                maxFps=MAX_FPS,
                bitrate=BITRATE,
                logLevel="warn",
            )

            try:
                streamServer: AdbConnection = await to_thread(
                    deployServer,
                    device,
                    cfg,
                    SERVER_PATH,
                    3000,
                )

            except Exception as ex:
                await self._raiseError("initialize.deploy", str(ex))
                raise

            if streamServer is None:
                await self._raiseError(
                    "initialize.deploy", "Failed to deploy scrcpy server"
                )
                raise RuntimeError("Failed to deploy scrcpy server")

            self._startServerLogDrain(streamServer)
            asyncLoop: AbstractEventLoop = get_running_loop()

            try:
                vSCKT: socket = await to_thread(
                    getSCRCPYADBSocket, device, cfg.Scid, 3000
                )
                self._vSocket = VideoSocket(vSCKT, loop=asyncLoop)

                cSCKT: socket = await to_thread(
                    getSCRCPYADBSocket, device, cfg.Scid, 3000
                )
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
                self.setSuppressEvent(False)

                self._streamServer = streamServer
                await self.asyncRaiseEvent("ON_INITIALIZED", self._codecContext)

            except Exception as ex:
                await self._raiseError("initialize.codec", str(ex))
                raise

        finally:
            self.setSuppressEvent(False)

    def start(self, *args, **kwargs):
        task: Task = None
        if self._streamServer is None:
            task = createTask(self.initialize, *args, **kwargs)

        if task is None:
            return super().start(*args, **kwargs)

        # add_done_callback only receives the finished task
        def _onInitDone(t: Task) -> None:
            try:
                t.result()
            except Exception as ex:
                warning(f"[SCRCPYEmitter] initialize failed id={self.id!r}: {ex}")
                return
            try:
                super(SCRCPYEmitter, self).start(*args, **kwargs)
            except Exception as ex:
                warning(f"[SCRCPYEmitter] start after init failed id={self.id!r}: {ex}")

        task.add_done_callback(_onInitDone)

    @property
    def isConnected(self) -> bool:
        return self._isRunning
