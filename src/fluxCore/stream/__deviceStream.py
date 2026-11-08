# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Lock
from functools import partial
from typing import Any, List, Optional

# ==================================================================================
from av import VideoCodecContext

# ==================================================================================
from fluxCore.types.interface.device import iDevice
from fluxCore.types.interface.emitters import iEmitter
from fluxCore.types.interface.packets import iImagePacket
from jAGFx.services import AsyncSubscription

# ==================================================================================
from ..types.interface.stream.__frameConsumer import iFrameConsumer
from .__frameDecoder import FrameDecoder
from .__presenter import Presenter
from .frameRing.__frameRing import FrameRing

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
    """In-process stream: one emitter, ring publish, registered frame consumers.

    ``_onFrame`` only publishes the packet into the ring (decode is scheduled
    inside ``FrameRing``). Presentation is owned by ``Presenter`` (default
    consumer); the stream does not decode to QImage or call the view.

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

    def __init__(self, ringSize: int = 8, displayFps: float = 30.0) -> None:
        super().__init__()
        self._ring = FrameRing(size=ringSize)
        self._decoder = FrameDecoder()
        self._consumers: List[iFrameConsumer] = []
        self._running: bool = False

        self._presenter = Presenter(displayFps=displayFps, name="StreamPresenter")
        self.registerConsumer(self._presenter)

        self._emitter: Optional[iEmitter] = None
        self._serial: Optional[str] = None
        self._desiredSerial: Optional[str] = None
        self._switchEpoch: int = 0
        self._switchLock = Lock()
        self._frameSubscribed: bool = False

    @classmethod
    def classname(cls) -> str:
        return cls.__name__

    # -------------------------------------------------------------------------
    # ring / default presenter
    # -------------------------------------------------------------------------
    @property
    def ring(self) -> FrameRing:
        return self._ring

    @property
    def presenter(self) -> Presenter:
        return self._presenter

    def attachView(self, view: Any) -> None:
        """Convenience: bind view to the default Presenter."""
        self._presenter.attachView(view)
        verbose(f"[{self.classname()}] attachView type={type(view).__name__}")

    def detachView(self) -> None:
        self._presenter.detachView()

    # -------------------------------------------------------------------------
    # consumers (iFrameConsumer)
    # -------------------------------------------------------------------------
    def registerConsumer(self, consumer: iFrameConsumer) -> None:
        if consumer in self._consumers:
            return
        consumer.attachRing(self._ring)
        self._consumers.append(consumer)
        if self._running:
            try:
                consumer.start()
            except Exception as ex:
                warning(f"[{self.classname()}] consumer.start failed: {ex}")
        verbose(
            f"[{self.classname()}] registerConsumer "
            f"type={type(consumer).__name__} n={len(self._consumers)}"
        )

    def unregisterConsumer(self, consumer: iFrameConsumer) -> None:
        if consumer not in self._consumers:
            return
        try:
            if getattr(consumer, "isRunning", False):
                consumer.stop()
        except Exception as ex:
            warning(f"[{self.classname()}] consumer.stop failed: {ex}")
        try:
            consumer.detachRing()
        except Exception as ex:
            warning(f"[{self.classname()}] consumer.detachRing failed: {ex}")
        self._consumers.remove(consumer)

    def _startConsumers(self) -> None:
        for consumer in list(self._consumers):
            try:
                if not getattr(consumer, "isRunning", False):
                    consumer.start()
            except Exception as ex:
                warning(
                    f"[{self.classname()}] start consumer "
                    f"{type(consumer).__name__} failed: {ex}"
                )

    def _stopConsumers(self) -> None:
        for consumer in list(self._consumers):
            try:
                if getattr(consumer, "isRunning", False):
                    consumer.stop()
            except Exception as ex:
                warning(
                    f"[{self.classname()}] stop consumer "
                    f"{type(consumer).__name__} failed: {ex}"
                )

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
        self._running = False
        self._stopConsumers()

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

        if self._frameSubscribed:
            try:
                emitter.unsubscribe(C_ON_FRAME, self._onFrame)
            except Exception:
                pass
            self._frameSubscribed = False

        emitter.subscribe(C_ON_FRAME, self._onFrame)
        self._frameSubscribed = True
        self._running = True
        self._startConsumers()

        if not emitter.isRunning:
            emitter.start()

        serial = getattr(emitter, "id", None)
        verbose(f"[{self.classname()}] start serial={serial!r}")

    async def _onFrame(self, packet: iImagePacket) -> None:
        """Publish only — decode is scheduled inside the ring; consumers pull."""
        try:
            codec: Optional[VideoCodecContext] = self._decoder.codec
            if codec is None:
                return

            self._ring.publish(packet, codec)
            # Optional fan-out for stream-level subscribers (packet, not Tensor).
            self.raiseEvent(C_ON_FRAME, packet)

        except Exception as ex:
            warning(f"[{self.classname()}] _onFrame failed: {ex}")

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
                await self.stop()
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
                    continue

                try:
                    self.attachedEmitter(emitter)
                    await self.start()
                except Exception as ex:
                    error(
                        f"[{self.classname()}] switchDevice attach/start "
                        f"failed serial={target!r}: {ex}"
                    )
                    await self.stop()
                    self.detachedEmitter()
                    self._serial = None
                    self.raiseEvent(C_ON_ERROR, ex)
                    if self._desiredSerial != target or self._switchEpoch != epochAtStart:
                        continue
                    return

                if self._desiredSerial != target or self._switchEpoch != epochAtStart:
                    verbose(
                        f"[{self.classname()}] switchDevice race after start; retry"
                    )
                    await self.stop()
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
