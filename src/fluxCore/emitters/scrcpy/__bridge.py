# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import Event
from importlib import import_module
from typing import TYPE_CHECKING, Any, Awaitable, Callable
from uuid import UUID

# ==================================================================================
from jAGFx.IPC import Bridge
from jAGFx.types.interface.communication import iMessage

# ==================================================================================
from ...devices import SCRCPY
from .__footprint import SCRCPYError
from .__messages import (
    ScrcpyErrorMessage,
    ScrcpyInitializeMessage,
    ScrcpyMetadataMessage,
    ScrcpyStartMessage,
    ScrcpyStopMessage,
)
from .__payloads import ScrcpyInitParams

# ==================================================================================
if TYPE_CHECKING:
    from .__SCRCPYEmitter import SCRCPYEmitter

# ==================================================================================
MetadataCallback = Callable[[SCRCPY], Awaitable[None] | None]
ErrorCallback = Callable[[SCRCPYError], Awaitable[None] | None]


def _loadSCRCPYEmitter():
    """Import SCRCPYEmitter without triggering class private-name mangling."""
    return import_module("fluxCore.emitters.scrcpy.__SCRCPYEmitter").SCRCPYEmitter


# ==================================================================================
class _ScrcpyBridgeBase(Bridge):
    """Shared send: leave ownerId unset so the peer routes to its default bridge."""

    async def send(self, message: iMessage) -> None:
        if self._endpoint is None:
            raise RuntimeError("Bridge has no attached Endpoint")
        await self._endpoint.send(message)


# ==================================================================================
class ScrcpyRealBridge(_ScrcpyBridgeBase):
    """Client-side bridge: owns emitter; handles Initialize / Start / Stop."""

    def __init__(self, emitter: Any | None = None) -> None:
        super().__init__()
        self._emitter: Any | None = emitter
        self._messageHandlers[ScrcpyInitializeMessage] = self._onInitialize
        self._messageHandlers[ScrcpyStartMessage] = self._onStart
        self._messageHandlers[ScrcpyStopMessage] = self._onStop
        self._invalidateHandlerCache()
        if self._emitter is not None:
            self._wireEmitter(self._emitter)

    @property
    def emitter(self) -> Any | None:
        return self._emitter

    def setEmitter(self, emitter: Any) -> None:
        self._emitter = emitter
        self._wireEmitter(emitter)

    def _wireEmitter(self, emitter: Any) -> None:
        if hasattr(emitter, "subscribe"):
            emitter.subscribe("ON_METADATA_UPDATE", self._onEmitterMetadata)
            emitter.subscribe("ON_ERROR", self._onEmitterError)

    async def _onEmitterMetadata(self, scrcpy: SCRCPY) -> None:
        await self.send(ScrcpyMetadataMessage(payload=scrcpy))

    async def _onEmitterError(self, err: SCRCPYError) -> None:
        await self.send(ScrcpyErrorMessage(payload=err))

    def _snapshot(self, params: ScrcpyInitParams) -> SCRCPY:
        SCRCPYEmitter = _loadSCRCPYEmitter()
        if isinstance(self._emitter, SCRCPYEmitter):
            return SCRCPYEmitter.toScrcpy(self._emitter)
        scrcpy = SCRCPY(serial=params.serial, name=getattr(self._emitter, "name", None))
        codecId = getattr(self._emitter, "codecId", "h264")
        width = int(getattr(self._emitter, "width", 0) or 0)
        height = int(getattr(self._emitter, "height", 0) or 0)
        scrcpy.update(codecId=codecId, width=width, height=height)
        return scrcpy

    async def _onInitialize(self, message: ScrcpyInitializeMessage) -> None:
        params = message.payload
        if not isinstance(params, ScrcpyInitParams):
            await self.send(
                ScrcpyErrorMessage(
                    payload=SCRCPYError(
                        phase="initialize",
                        message="missing ScrcpyInitParams",
                        serial=None,
                    ),
                    correlationId=message.correlationId,
                    isTerminal=True,
                )
            )
            return

        try:
            if self._emitter is None:
                SCRCPYEmitter = _loadSCRCPYEmitter()
                self._emitter = SCRCPYEmitter(serial=params.serial)
                self._wireEmitter(self._emitter)

            await self._emitter.initialize(
                GPUID=params.gpuId, GPUReady=params.gpuReady
            )
            snapshot = self._snapshot(params)
            await self.send(
                ScrcpyMetadataMessage(
                    payload=snapshot,
                    correlationId=message.correlationId,
                    isTerminal=True,
                )
            )
        except Exception as ex:
            await self.send(
                ScrcpyErrorMessage(
                    payload=SCRCPYError(
                        phase="initialize",
                        message=str(ex),
                        serial=params.serial,
                    ),
                    correlationId=message.correlationId,
                    isTerminal=True,
                )
            )

    async def _onStart(self, message: ScrcpyStartMessage) -> None:
        if self._emitter is None:
            return
        self._emitter.start()

    async def _onStop(self, message: ScrcpyStopMessage) -> None:
        if self._emitter is None:
            return
        self._emitter.stop()


# ==================================================================================
class ScrcpyProxyBridge(_ScrcpyBridgeBase):
    """Main-side bridge: sends commands; receives Metadata / Error."""

    def __init__(self) -> None:
        super().__init__()
        self._onMetadata: MetadataCallback | None = None
        self._onError: ErrorCallback | None = None
        self._lastMetadata: SCRCPY | None = None
        self._lastError: SCRCPYError | None = None
        self._metadataEvent: Event = Event()
        self._errorEvent: Event = Event()

        self._messageHandlers[ScrcpyMetadataMessage] = self._onMetadataMessage
        self._messageHandlers[ScrcpyErrorMessage] = self._onErrorMessage
        self._invalidateHandlerCache()

    @property
    def lastMetadata(self) -> SCRCPY | None:
        return self._lastMetadata

    @property
    def lastError(self) -> SCRCPYError | None:
        return self._lastError

    @property
    def metadataEvent(self) -> Event:
        return self._metadataEvent

    @property
    def errorEvent(self) -> Event:
        return self._errorEvent

    def setMetadataHandler(self, callback: MetadataCallback | None) -> None:
        self._onMetadata = callback

    def setErrorHandler(self, callback: ErrorCallback | None) -> None:
        self._onError = callback

    async def requestInitialize(
        self,
        params: ScrcpyInitParams,
        *,
        correlationId: UUID | None = None,
    ) -> ScrcpyInitializeMessage:
        msg = ScrcpyInitializeMessage(payload=params, correlationId=correlationId)
        assert msg.correlationId is not None

        async def _processor(reply: iMessage) -> None:
            # Bridge prioritizes processors over type handlers; forward so
            # Metadata/Error handlers still run for this correlation.
            handler = self._resolveHandler(reply)
            if handler is not None:
                result = handler(reply)
                if result is not None:
                    await result

        self.registerProcessor(msg.correlationId, _processor)
        await self.send(msg)
        return msg

    async def requestStart(self) -> None:
        await self.send(ScrcpyStartMessage())

    async def requestStop(self) -> None:
        await self.send(ScrcpyStopMessage())

    async def _onMetadataMessage(self, message: ScrcpyMetadataMessage) -> None:
        payload = message.payload
        if isinstance(payload, SCRCPY):
            self._lastMetadata = payload
            self._metadataEvent.set()
            if self._onMetadata is not None:
                result = self._onMetadata(payload)
                if result is not None:
                    await result

    async def _onErrorMessage(self, message: ScrcpyErrorMessage) -> None:
        payload = message.payload
        if isinstance(payload, SCRCPYError):
            self._lastError = payload
            self._errorEvent.set()
            if self._onError is not None:
                result = self._onError(payload)
                if result is not None:
                    await result


# ==================================================================================
__all__ = ["ScrcpyRealBridge", "ScrcpyProxyBridge"]
