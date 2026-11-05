# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Lock
from functools import partial
from typing import Any, List, Optional, Tuple

# ==================================================================================
from PySide6.QtGui import QImage

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.emitters import iEmitter
from fluxCore.types.interface.packets import iFrame
from jAGFx.services import AsyncSubscription

# ==================================================================================
from .__eDecodeFormat import eDecodeFormat
from .__frameDecoder import FrameDecoder
from .__frameFlags import FrameFlags
from .__frameHeader import FrameHeader
from .__frameRing import FrameRing
from .__streamPresenter import StreamPresenter

# ==================================================================================
C_ON_FRAME: str = "ON_FRAME"
C_ON_METADATA_UPDATE: str = "ON_METADATA_UPDATE"
C_ON_ERROR: str = "ON_ERROR"
C_ON_INITIALIZED: str = "ON_INITIALIZED"

C_ON_STARTING: str = "ON_STARTING"
C_ON_STARTED: str = "ON_STARTED"
C_ON_STOPPING: str = "ON_STOPPING"
C_ON_STOPPED: str = "ON_STOPPED"
C_ON_PAUSED: str = "ON_PAUSED"
C_ON_RESUMED: str = "ON_RESUMED"

# Lifecycle events re-raised from the emitter; ON_FRAME is handled by _onFrame only.
C_LIFECYCLE_EVENTS: List[str] = [
    C_ON_METADATA_UPDATE,
    C_ON_ERROR,
    C_ON_INITIALIZED,
    C_ON_STARTING,
    C_ON_STARTED,
    C_ON_STOPPING,
    C_ON_STOPPED,
    C_ON_PAUSED,
    C_ON_RESUMED,
]
# ==================================================================================


# ==================================================================================
class LocalDeviceStream(AsyncSubscription):
    """In-process stream: one emitter, decode once, ring + optional view present.

    Device switches go through ``switchDevice`` (serialized). Consumers should not
    subscribe to the emitter directly.
    """

    EVENTS: List[str] = [
        C_ON_FRAME,
        C_ON_METADATA_UPDATE,
        C_ON_ERROR,
        C_ON_INITIALIZED,
        C_ON_STARTING,
        C_ON_STARTED,
        C_ON_STOPPING,
        C_ON_STOPPED,
        C_ON_PAUSED,
        C_ON_RESUMED,
    ]

    def __init__(self, ringSize: int = 8) -> None:
        super().__init__()
        self._decoder = FrameDecoder()
        self._emitter: Optional[iEmitter] = None
        self._ring = FrameRing(ringSize)
        self._presenter = StreamPresenter()
        self._view: Any = None
        self._switchLock = Lock()
        self._serial: Optional[str] = None
        self._previousSize: Tuple[int, int] = (0, 0)
        self._frameSubscribed: bool = False

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    # --------------------------------------------------------------------------
    # view
    # -------------------------------------------------------------------------
    def attachView(self, view: Any) -> None:
        self._view = view
        verbose(f"[{self.classname()}] attachView type={type(view).__name__}")

    def detachView(self) -> None:
        self._view = None

    # -------------------------------------------------------------------------
    # emitter wiring
    # -------------------------------------------------------------------------
    async def _onEvent(self, event: str, *args, **kwargs) -> None:
        self.raiseEvent(event, *args, **kwargs)

    def attachedEmitter(self, emitter: iEmitter) -> None:
        if emitter is None:
            raise ValueError("emitter is required")

        try:
            emitter.setSuppressEvent(True)
            decoder: FrameDecoder = self._decoder

            emitter.subscribe(C_ON_INITIALIZED, decoder.setCodecContext)
            for event in C_LIFECYCLE_EVENTS:
                if event == C_ON_INITIALIZED:
                    continue
                callback = partial(self._onEvent, event)
                emitter.subscribe(event, callback)

            self._emitter = emitter

        except Exception:
            raise

        finally:
            emitter.setSuppressEvent(False)

    def detachedEmitter(self) -> None:
        emitter: Optional[iEmitter] = self._emitter
        if emitter is None:
            return

        try:
            emitter.setSuppressEvent(True)
            decoder: FrameDecoder = self._decoder

            emitter.unsubscribe(C_ON_INITIALIZED, decoder.setCodecContext)
            if self._frameSubscribed:
                try:
                    emitter.unsubscribe(C_ON_FRAME, self._onFrame)
                except Exception:
                    pass
                self._frameSubscribed = False

            for event in C_LIFECYCLE_EVENTS:
                callbacks = list(emitter._callbacks.get(event, []))
                for callback in callbacks:
                    if (
                        isinstance(callback, partial)
                        and callback.func == self._onEvent
                    ):
                        emitter.unsubscribe(event, callback)

        except Exception:
            raise

        finally:
            self._emitter = None

    async def stop(self) -> None:
        emitter: Optional[iEmitter] = self._emitter
        if emitter is None:
            return
        if getattr(emitter, "isRunning", False):
            emitter.stop()

    async def start(self) -> None:
        emitter: Optional[iEmitter] = self._emitter
        if emitter is None:
            raise ValueError("No emitter attached")

        if self._decoder is None:
            raise ValueError("Decoder not set")

        self._previousSize = (0, 0)

        if self._frameSubscribed:
            try:
                emitter.unsubscribe(C_ON_FRAME, self._onFrame)
            except Exception:
                pass
            self._frameSubscribed = False

        emitter.subscribe(C_ON_FRAME, self._onFrame)
        self._frameSubscribed = True

        if not emitter.isRunning:
            emitter.start()

        serial = getattr(emitter, "id", None)
        verbose(f"[{self.classname()}] start serial={serial!r}")

    async def _onFrame(self, frame: iFrame) -> None:
        try:
            prevSize: Tuple[int, int] = self._previousSize
            decoder: FrameDecoder = self._decoder

            qimg: QImage = decoder.decode(frame, eDecodeFormat.QIMAGE)
            if qimg is None or qimg.isNull():
                return

            newSize: Tuple[int, int] = (qimg.width(), qimg.height())

            flag: FrameFlags = FrameFlags.NONE
            if getattr(frame, "isKeyFrame", False):
                flag |= FrameFlags.KEYFRAME
            if newSize != prevSize:
                emitter = self._emitter
                if emitter is not None and hasattr(emitter, "toDevice"):
                    device: iDevice = emitter.toDevice(emitter)
                    self.raiseEvent(C_ON_METADATA_UPDATE, device)
                flag |= FrameFlags.RESOLUTION_CHANGED

            header: FrameHeader = FrameHeader(
                pts=getattr(frame, "pts", 0),
                width=newSize[0],
                height=newSize[1],
                format=eDecodeFormat.QIMAGE,
                flags=flag,
            )

            self._previousSize = newSize
            self._ring.publish(header, qimg)
            self._presentLatest()
            self.raiseEvent(C_ON_FRAME, header, qimg)

        except Exception as ex:
            warning(f"[{self.classname()}] _onFrame failed", ex)

    def _presentLatest(self) -> None:
        view = self._view
        if view is None:
            return

        latest = self._ring.latest()
        if latest is None:
            return

        header, image = latest
        meta = {
            "seq": header.sequence,
            "pts": header.pts,
            "w": header.width,
            "h": header.height,
        }

        if hasattr(view, "presentExternal"):
            self._presenter.present(view, meta, image)
            return

        try:
            view.image = image
        except Exception as ex:
            warning(f"[{self.classname()}] present fallback failed: {ex}")

    # -------------------------------------------------------------------------
    # device switch (page entry point)
    # -------------------------------------------------------------------------
    async def switchDevice(self, deviceManager: Any, serial: Optional[str]) -> None:
        """Serialize detach/stop → ensureRunning → attach/start for one serial."""
        async with self._switchLock:
            cleaned: Optional[str] = (serial or "").strip() or None
            if cleaned == self._serial and self._emitter is not None:
                return

            await self._detachAndStop()

            if cleaned is None:
                self._serial = None
                verbose(f"[{self.classname()}] switchDevice cleared")
                return

            if deviceManager is None:
                raise ValueError("deviceManager is required")

            ensure = getattr(deviceManager, "ensureRunning", None)
            if ensure is None:
                raise TypeError(
                    f"deviceManager {type(deviceManager).__name__} has no ensureRunning"
                )

            emitter = await ensure(cleaned)
            self.attachedEmitter(emitter)
            await self.start()
            self._serial = cleaned
            verbose(f"[{self.classname()}] switchDevice serial={cleaned!r}")

    async def _detachAndStop(self) -> None:
        emitter: Optional[iEmitter] = self._emitter
        self.detachedEmitter()
        if emitter is not None and getattr(emitter, "isRunning", False):
            try:
                emitter.stop()
            except Exception as ex:
                warning(f"[{self.classname()}] stop failed: {ex}")
        self._serial = None


# ==================================================================================
__all__ = ["LocalDeviceStream"]
