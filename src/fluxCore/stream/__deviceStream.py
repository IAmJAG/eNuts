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
from ..types.__eDecodeFormat import eDecodeFormat
from .__frameDecoder import FrameDecoder
from .__frameFlags import FrameFlags
from .__frameHeader import FrameHeader
from .__frameRing import FrameRing
from .__streamPresenter import StreamPresenter

# ==================================================================================
try:
    from shiboken6 import isValid as _qtIsValid
except ImportError:  # pragma: no cover
    def _qtIsValid(obj: Any) -> bool:  # type: ignore[misc]
        return obj is not None

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

    ``switchDevice`` is coalesced: rapid combo changes only apply the **latest**
    serial. In-flight ``ensureRunning`` work for a superseded serial is abandoned
    after it returns (no attach/start). Previous emitters are hot-retained unless
    ``stopPrevious=True`` or ``serial=None``.
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
        self._ring = FrameRing(size=ringSize)
        self._decoder = FrameDecoder()
        self._presenter = StreamPresenter()
        self._view: Any = None
        self._emitter: Optional[iEmitter] = None
        self._serial: Optional[str] = None
        self._desiredSerial: Optional[str] = None
        self._switchEpoch: int = 0
        self._switchLock = Lock()
        self._frameSubscribed: bool = False
        self._previousSize: Tuple[int, int] = (0, 0)

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    # -------------------------------------------------------------------------
    # view
    # -------------------------------------------------------------------------
    def attachView(self, view: Any) -> None:
        self._view = view
        verbose(f"[{self.classname()}] attachView type={type(view).__name__}")

    def detachView(self) -> None:
        self._view = None

    # -------------------------------------------------------------------------
    # codec
    # -------------------------------------------------------------------------
    def _syncCodecFromEmitter(self, emitter: iEmitter) -> None:
        codec = getattr(emitter, "_codecContext", None)
        if codec is None:
            return
        self._decoder.setCodecContext(codec)
        verbose(
            f"[{self.classname()}] codec synced from emitter "
            f"id={getattr(emitter, 'id', None)!r}"
        )

    def _clearCodec(self) -> None:
        self._decoder.setCodecContext(None)

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
            self._syncCodecFromEmitter(emitter)

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
                    try:
                        emitter.unsubscribe(event, callback)
                    except Exception:
                        pass

            self._emitter = None
            self._clearCodec()

        finally:
            try:
                emitter.setSuppressEvent(False)
            except Exception:
                pass

    async def stop(self) -> None:
        emitter = self._emitter
        if emitter is None:
            return

        if self._frameSubscribed:
            try:
                emitter.unsubscribe(C_ON_FRAME, self._onFrame)
            except Exception:
                pass
            self._frameSubscribed = False

        serial = getattr(emitter, "id", None)
        verbose(f"[{self.classname()}] stop serial={serial!r}")

    async def start(self) -> None:
        emitter = self._emitter
        if emitter is None:
            return

        if self._decoder is None:
            return

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
            decoder: FrameDecoder = self._decoder
            if decoder.codec is None:
                return

            prevSize: Tuple[int, int] = self._previousSize

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
        if not _qtIsValid(view):
            # Page/widget destroyed while emitter still streaming.
            self._view = None
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
        except RuntimeError as ex:
            if "already deleted" in str(ex).lower():
                self._view = None
                return
            warning(f"[{self.classname()}] present fallback failed: {ex}")
        except Exception as ex:
            warning(f"[{self.classname()}] present fallback failed: {ex}")

    # -------------------------------------------------------------------------
    # device switch (page entry point)
    # -------------------------------------------------------------------------
    async def switchDevice(
        self,
        deviceManager: Any,
        serial: Optional[str],
        stopPrevious: bool = False,
    ) -> None:
        """Request a device switch; only the latest serial is applied.

        Concurrent calls update ``_desiredSerial`` and bump ``_switchEpoch``.
        The single worker under ``_switchLock`` loops until the active target
        matches the latest desired serial, skipping attach for superseded work.
        """
        cleaned: Optional[str] = (serial or "").strip() or None
        self._desiredSerial = cleaned
        self._switchEpoch += 1
        requestEpoch = self._switchEpoch

        verbose(
            f"[{self.classname()}] switchDevice request serial={cleaned!r} "
            f"epoch={requestEpoch}"
        )

        async with self._switchLock:
            # Another waiter may have already satisfied a newer epoch.
            if requestEpoch != self._switchEpoch:
                verbose(
                    f"[{self.classname()}] switchDevice superseded "
                    f"epoch={requestEpoch} current={self._switchEpoch}"
                )
                return

            while True:
                target = self._desiredSerial
                epochAtStart = self._switchEpoch

                if target == self._serial and self._emitter is not None:
                    verbose(
                        f"[{self.classname()}] switchDevice already on "
                        f"serial={target!r}"
                    )
                    return

                prev = self._emitter
                self.detachedEmitter()

                if (stopPrevious or target is None) and prev is not None:
                    if getattr(prev, "isRunning", False):
                        try:
                            prev.stop()
                        except Exception as ex:
                            warning(
                                f"[{self.classname()}] stop previous failed: {ex}"
                            )

                self._serial = None

                if target is None:
                    verbose(f"[{self.classname()}] switchDevice cleared")
                    return

                if deviceManager is None:
                    raise ValueError("deviceManager is required")

                ensure = getattr(deviceManager, "ensureRunning", None)
                if ensure is None:
                    raise TypeError(
                        f"deviceManager {type(deviceManager).__name__} "
                        f"has no ensureRunning"
                    )

                # Long wait: user may change selection while this runs.
                # Connection / init failures must not escape as unretrieved tasks
                # (createTask has no caller await).
                try:
                    emitter = await ensure(target)
                except Exception as ex:
                    error(
                        f"[{self.classname()}] switchDevice ensureRunning "
                        f"failed serial={target!r}: {ex}"
                    )
                    self.raiseEvent(C_ON_ERROR, ex)
                    if self._desiredSerial != target or self._switchEpoch != epochAtStart:
                        continue
                    return

                if self._desiredSerial != target or self._switchEpoch != epochAtStart:
                    verbose(
                        f"[{self.classname()}] switchDevice abandoned "
                        f"target={target!r} desired={self._desiredSerial!r} "
                        f"epoch={epochAtStart}->{self._switchEpoch}"
                    )
                    # Do not attach the stale emitter; loop for the new target.
                    continue

                try:
                    self.attachedEmitter(emitter)
                    await self.start()
                except Exception as ex:
                    error(
                        f"[{self.classname()}] switchDevice attach/start "
                        f"failed serial={target!r}: {ex}"
                    )
                    self.detachedEmitter()
                    self._serial = None
                    self.raiseEvent(C_ON_ERROR, ex)
                    if self._desiredSerial != target or self._switchEpoch != epochAtStart:
                        continue
                    return

                if self._desiredSerial != target or self._switchEpoch != epochAtStart:
                    # Desired changed during attach/start — detach and retry.
                    verbose(
                        f"[{self.classname()}] switchDevice race after start; retry"
                    )
                    self.detachedEmitter()
                    self._serial = None
                    continue

                self._serial = target
                verbose(
                    f"[{self.classname()}] switchDevice applied serial={target!r} "
                    f"running={getattr(emitter, 'isRunning', None)}"
                )
                return


# ==================================================================================
__all__ = ["LocalDeviceStream"]
