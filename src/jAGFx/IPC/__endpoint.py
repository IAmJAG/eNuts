# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Event, Task, create_task, to_thread
from asyncio import Queue as AsyncQueue
from queue import Empty
from typing import Any, Callable, Type
from uuid import UUID

# ==================================================================================
from ..types.interface.communication import iBridge, iEndpoint, iIOQueue, iMessage


# ==================================================================================
class Endpoint(iEndpoint):
    C_RECEIVE_TIMEOUT: float = 0.01

    def __init__(self, ioQueue: iIOQueue) -> None:
        self._ioQueue: iIOQueue = ioQueue
        self._outbound: AsyncQueue[iMessage] | None = None
        self._inboundTask: Task | None = None
        self._outboundTask: Task | None = None
        self._stopping: Event = Event()
        self._started: bool = False

        self._kindToBridge: dict[Any, iBridge] = {}
        self._bridgeKinds: dict[iBridge, set[Any]] = {}
        self._correlations: dict[UUID, iBridge] = {}

    @property
    def isStarted(self) -> bool:
        return self._started

    async def start(self) -> None:
        if self._started:
            raise RuntimeError("Endpoint is already started")

        self._stopping.clear()
        self._outbound = AsyncQueue()
        self._inboundTask = create_task(self._pollInbound(), name="Endpoint.inbound")
        self._outboundTask = create_task(self._drainOutbound(), name="Endpoint.outbound")
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return

        self._stopping.set()

        for task in (self._inboundTask, self._outboundTask):
            if task is not None and not task.done():
                task.cancel()

        for task in (self._inboundTask, self._outboundTask):
            if task is not None:
                try:
                    await task
                except CancelledError:
                    pass

        self._inboundTask = None
        self._outboundTask = None
        self._outbound = None
        self._started = False

    async def send(self, message: iMessage) -> None:
        if not self._started or self._outbound is None:
            raise RuntimeError("Endpoint is not started")

        if message.isTerminal:
            self._unmapCorrelation(message.correlationId)

        await self._outbound.put(message)

    def registerBridge(self, bridge: iBridge) -> None:
        kinds = set(bridge.messageHandlers.keys())
        for kind in kinds:
            if kind in self._kindToBridge:
                raise ValueError(
                    f"Message kind '{kind}' is already registered by another bridge"
                )

        for kind in kinds:
            self._kindToBridge[kind] = bridge

        self._bridgeKinds[bridge] = kinds
        bridge.attachEndpoint(self)

    def unregisterBridge(self, bridge: iBridge) -> None:
        kinds = self._bridgeKinds.pop(bridge, set())
        for kind in kinds:
            if self._kindToBridge.get(kind) is bridge:
                del self._kindToBridge[kind]

        stale = [cid for cid, b in self._correlations.items() if b is bridge]
        for cid in stale:
            del self._correlations[cid]

        bridge.detachEndpoint()

    def bindCorrelation(self, correlationId: UUID, bridge: iBridge) -> None:
        self._correlations[correlationId] = bridge

    def unbindCorrelation(self, correlationId: UUID) -> None:
        self._correlations.pop(correlationId, None)

    def hasCorrelation(self, correlationId: UUID) -> bool:
        return correlationId in self._correlations

    def _unmapCorrelation(self, correlationId: UUID | None) -> None:
        if correlationId is None:
            return

        bridge = self._correlations.pop(correlationId, None)
        if bridge is not None:
            bridge.unregisterProcessor(correlationId)

    async def _pollInbound(self) -> None:
        timeOut: float = self.C_RECEIVE_TIMEOUT
        receive: Callable[[float | None], Any] = self._ioQueue.receive
        isSet: Callable[[], bool] = self._stopping.is_set

        while not isSet():
            try:
                message = await to_thread(receive, timeOut)

            except Empty:
                continue
            except CancelledError:
                break
            except Exception:
                if isSet():
                    break
                continue

            try:
                await self._onInbound(message)

            except CancelledError:
                break
            except Exception:
                continue

    async def _drainOutbound(self) -> None:
        outbound = self._outbound
        if outbound is None:
            return

        send: Callable[[iMessage], None] = self._ioQueue.send
        isSet: Callable[[], bool] = self._stopping.is_set

        while not isSet():
            try:
                message = await outbound.get()

            except CancelledError:
                break

            try:
                await to_thread(send, message)

            except CancelledError:
                break

            except Exception:
                if isSet():
                    break
                continue

    async def _onInbound(self, message: iMessage) -> None:
        bridge = self._resolveBridge(message)
        if bridge is None:
            return

        await bridge.handleMessage(message)

        if message.isTerminal:
            self._unmapCorrelation(message.correlationId)
        elif message.correlationId is not None:
            self.bindCorrelation(message.correlationId, bridge)

    def _resolveBridge(self, message: iMessage) -> iBridge | None:
        correlationId = message.correlationId
        if correlationId is not None:
            bridge = self._correlations.get(correlationId)
            if bridge is not None:
                return bridge

        # Handlers are keyed by message type (see Bridge.messageHandlers).
        kind: Type[iMessage] | type = type(message)
        return self._kindToBridge.get(kind)


# ==================================================================================
__all__ = ["Endpoint"]
