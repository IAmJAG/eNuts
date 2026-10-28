# ==================================================================================
from __future__ import annotations

# ==================================================================================
from asyncio import CancelledError, Event, Task, create_task, to_thread
from asyncio import Queue as AsyncQueue
from queue import Empty
from typing import Any, Callable
from uuid import UUID

# ==================================================================================
from ..types.interface.communication import iBridge, iEndpoint, iIOQueue, iMessage


# ==================================================================================
class Endpoint(iEndpoint):
    """Process-local IPC endpoint.

    Owns the IOQueue adapter and routes inbound messages to Bridges by
    ``message.ownerId``. Correlation lifecycle is entirely Bridge-owned.
    """

    C_RECEIVE_TIMEOUT: float = 0.01

    def __init__(self, ioQueue: iIOQueue) -> None:
        self._ioQueue: iIOQueue = ioQueue
        self._outbound: AsyncQueue[iMessage] | None = None
        self._inboundTask: Task | None = None
        self._outboundTask: Task | None = None
        self._stopping: Event = Event()
        self._started: bool = False

        self._bridges: dict[UUID, iBridge] = {}
        self._defaultBridgeId: UUID | None = None

    @property
    def isStarted(self) -> bool:
        return self._started

    @property
    def defaultBridgeId(self) -> UUID | None:
        return self._defaultBridgeId

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

        await self._outbound.put(message)

    def registerBridge(self, bridge: iBridge, *, asDefault: bool = False) -> None:
        bridgeId = bridge.bridgeId
        if bridgeId in self._bridges:
            raise ValueError(f"Bridge ID '{bridgeId}' is already registered")

        self._bridges[bridgeId] = bridge
        bridge.attachEndpoint(self)

        if asDefault:
            self._defaultBridgeId = bridgeId

    def unregisterBridge(self, bridge: iBridge) -> None:
        bridgeId = bridge.bridgeId
        if self._bridges.get(bridgeId) is not bridge:
            return

        del self._bridges[bridgeId]
        if self._defaultBridgeId == bridgeId:
            self._defaultBridgeId = None

        bridge.detachEndpoint()

    def _resolveBridge(self, message: iMessage) -> iBridge | None:
        ownerId = message.ownerId
        if ownerId is None:
            if self._defaultBridgeId is None:
                return None
            return self._bridges.get(self._defaultBridgeId)

        return self._bridges.get(ownerId)

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
            # Unknown owner or missing default — drop (routing error).
            return

        await bridge.handleMessage(message)


# ==================================================================================
__all__ = ["Endpoint"]
