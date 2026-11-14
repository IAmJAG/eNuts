# ==================================================================================
from __future__ import annotations

# ==================================================================================
import os

# ==================================================================================
from asyncio import (
    AbstractEventLoop,
    CancelledError,
    Task,
    get_running_loop,
    to_thread,
    wait_for,
)
from asyncio import (
    TimeoutError as AsyncTimeoutError,
)
from asyncio import (
    sleep as asyncSleep,
)
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
from ..configurations.scrcpy import SCRCPYConfig
from ..devices import SCRCPY
from ..packets import TensorPacket
from ..sockets import ControlSocket, VideoSocket
from ..types.interface.device import iDevice
from ..types.interface.packets import iImagePacket
from ..types.interface.sockets import iControlSocket, iVideoSocket
from ..utilities.pyav import createCodecContext
from ..utilities.scrcpy import deployServer, getSCRCPYADBSocket

# ==================================================================================
C_METADATA_TIMEOUT_S: float = 15.0
# ==================================================================================


# ==================================================================================
class SCRCPYEmitter(AsyncService, SCRCPY):
    def __init__(
            self, serial: str, name: Optional[str] = None, options: Optional[SCRCPYConfig] = None
        ) -> None:

        AsyncService.__init__(self, work=self.work, name=name)
        SCRCPY.__init__(self, serial=serial, name=name)
        AsyncSubscription.__init__(self)

        self._options: SCRCPYConfig = options or SCRCPYConfig()

        self._vSocket: Optional[iVideoSocket] = None
        self._cSocket: Optional[iControlSocket] = None
        self._streamServer: Optional[AdbConnection] = None
        self._codecContext: Optional[VideoCodecContext] = None
        self._serverLogThread: Optional[Thread] = None
        self._serverLogStop: ThreadEvent = ThreadEvent()
        self._adbDevice: Optional[AdbDevice] = None

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
                    except Exception as ex:
                        trace(f"server log read failed id={self.id!r} err={ex!r}")
                        break
                    if not lChunk:
                        trace(f"server log eof id={self.id!r}")
                        break
                    text = lChunk.decode("utf-8", errors="replace").rstrip()
                    if text:
                        trace(f"server id={self.id!r} {text}")
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

    async def _dumpDiagnostics(self, tag: str = "metadata-timeout") -> None:
        """logcat + process list after a metadata stall."""
        device = self._adbDevice
        if device is None:
            return

        def _shell(cmd: str) -> str:
            try:
                return (device.shell(cmd) or "").strip()
            except Exception as ex:
                return f"<shell failed {ex!r}>"

        try:
            ps = await to_thread(
                _shell,
                "ps -A 2>/dev/null | grep -E 'app_process|scrcpy' || ps | grep -E 'app_process|scrcpy' || true",
            )
            for line in (ps or "(no matching process)").splitlines()[:20]:
                trace(f"ps[{tag}] id={self.id!r} {line}")
        except Exception as ex:
            trace(f"ps[{tag}] id={self.id!r} failed err={ex!r}")

        try:
            text = await to_thread(_shell, "logcat -d -t 120")
            if text:
                lines = text.splitlines()
                interesting = [
                    ln
                    for ln in lines
                    if any(
                        k in ln.lower()
                        for k in ("scrcpy", "androidruntime", "fatal", "exception", "codec", "media")
                    )
                ]
                chosen = interesting[-50:] if interesting else lines[-30:]
                for line in chosen:
                    trace(f"logcat[{tag}] id={self.id!r} {line}")
            else:
                trace(f"logcat[{tag}] id={self.id!r} (empty)")
        except Exception as ex:
            trace(f"logcat[{tag}] id={self.id!r} failed err={ex!r}")

    async def work(self, *args, **kwargs):
        sckt: iVideoSocket = self._vSocket
        if sckt is None:
            return
        n = 0
        try:
            while self.isRunning:
                try:
                    frame: iImagePacket = await sckt.asyncReceiveSingleFrame()
                    n += 1
                    if n <= 3 or n % 30 == 0:
                        trace(
                            f"frame id={self.id!r} n={n} bytes={len(frame.payload)} "
                            f"config={frame.isConfig} key={frame.isKeyFrame}"
                        )
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

    async def _recvExact(
        self, sckt: iVideoSocket, numBytes: int, phase: str, timeout: float
    ) -> bytes:
        try:
            return await wait_for(sckt.receive(numBytes), timeout=timeout)
        except AsyncTimeoutError as ex:
            raise ConnectionError(
                f"metadata {phase}: timed out after {timeout:.1f}s "
                f"waiting for {numBytes}B id={self.id!r}"
            ) from ex

    async def _probePartial(self, sckt: iVideoSocket) -> None:
        try:
            raw = getattr(sckt, "_socket", None)
            loop = getattr(sckt, "_loop", None)
            if raw is None or loop is None:
                return

            async def _once() -> bytes:
                return await loop.sock_recv(raw, 256)

            chunk = await wait_for(_once(), timeout=0.3)
            trace(
                f"metadata probe id={self.id!r} partial={len(chunk)}B "
                f"head={chunk[:16]!r}"
            )
        except Exception as ex:
            trace(f"metadata probe id={self.id!r} none err={type(ex).__name__}")

    async def _updateMetadata(
        self,
        sckt: iVideoSocket,
        timeout: float = C_METADATA_TIMEOUT_S,
        *,
        tunnelForward: bool = True,
    ) -> None:
        trace(
            f"metadata begin id={self.id!r} timeout={timeout:.1f}s "
            f"tunnelForward={tunnelForward}"
        )

        try:
            if tunnelForward:
                dummy = await self._recvExact(sckt, 1, "dummy", timeout)
                trace(f"metadata dummy id={self.id!r} byte={dummy[0]!r}")

            deviceName: bytes = await self._recvExact(sckt, 64, "deviceName", timeout)
            if deviceName and deviceName[0] == 0x00:
                deviceName = deviceName[1:] + await self._recvExact(
                    sckt, 1, "deviceName.pad", timeout
                )

            codecIdRaw: bytes = await self._recvExact(sckt, 4, "codecId", timeout)
            widthRaw: bytes = await self._recvExact(sckt, 4, "width", timeout)
            heightRaw: bytes = await self._recvExact(sckt, 4, "height", timeout)

        except ConnectionError:
            await self._probePartial(sckt)
            await self._dumpDiagnostics("metadata-timeout")
            raise

        lCodecId: str = (
            codecIdRaw.decode("ascii", errors="replace").strip("\x00") or "h264"
        )

        lWidth: int = int.from_bytes(widthRaw, "big")
        lHeight: int = int.from_bytes(heightRaw, "big")
        lName: str = deviceName.split(b"\x00", 1)[0].decode("utf-8", errors="replace")
        self._name = lName

        self.update(codecId=lCodecId, width=lWidth, height=lHeight)
        headerBytes = (1 if tunnelForward else 0) + len(deviceName) + 12
        trace(
            f"metadata id={self.id!r} name={lName!r} codec={lCodecId!r} "
            f"{lWidth}x{lHeight} header={headerBytes}B"
        )

        me: SCRCPY = self.toSCRCPY(self)
        await self.asyncRaiseEvent("ON_METADATA_UPDATE", me)

    async def initialize(self, GPUID: int = 0, GPUReady: bool = True) -> None:
        try:
            self.setSuppressEvent(True)

            device: AdbDevice = await to_thread(adb.device, serial=self.id)
            self._adbDevice = device
            cfg: SCRCPYConfig = self._options
            cfg.logLevel = "info"
            # Diagnostic path for Android 9 AVD: no control, no cleanup child,
            # modest max_size so encoder setup is lighter if it runs before meta.
            cfg.control = False
            cfg.cleanup = False
            cfg.audio = False
            if not cfg.maxSize:cfg.maxSize = 1024
            tunnelForward = bool(cfg.tunnelForward)
            wantControl = bool(cfg.control)
            trace(
                f"initialize id={self.id!r} field_scid={cfg._scid!r} "
                f"before deploy control={wantControl} cleanup={cfg.cleanup} "
                f"maxSize={cfg.maxSize}"
            )

            try:
                try:
                    await to_thread(device.shell, "logcat -c")
                except Exception:
                    pass

                streamServer: AdbConnection = await to_thread(
                    deployServer, device, cfg, cfg.serverPath, 3000,
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
            await asyncSleep(0.05)
            asyncLoop: AbstractEventLoop = get_running_loop()

            try:
                trace(
                    f"initialize id={self.id!r} socket scid={cfg.scid!r} "
                    f"field_scid={cfg._scid!r} tunnelForward={tunnelForward} "
                    f"control={wantControl}"
                )
                vSCKT: socket = await to_thread(
                    getSCRCPYADBSocket, device, cfg.scid, 3000
                )
                self._vSocket = VideoSocket(
                    vSCKT, loop=asyncLoop, packetType=TensorPacket
                )
                trace(f"initialize video socket id={self.id!r} ok")

                if wantControl:
                    cSCKT: socket = await to_thread(
                        getSCRCPYADBSocket, device, cfg.scid, 3000
                    )
                    self._cSocket = ControlSocket(cSCKT, loop=asyncLoop)
                    trace(f"initialize control socket id={self.id!r} ok")

                await self._updateMetadata(
                    self._vSocket, tunnelForward=tunnelForward
                )

            except Exception as ex:
                await self._raiseError("initialize.socket", str(ex))
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
